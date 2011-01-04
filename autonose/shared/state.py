import os
import sys
import logging
import threading
import Queue as queue

from file_state import FileState
import file_util
from const import cwd as base

log = logging.getLogger(__name__)
debug = log.debug
info = logging.getLogger(__name__ + '.summary').info

# TODO: shut up about unfound imports
#logging.getLogger(snakefood.find.logname).setLevel(logging.ERROR)

def union(*sets):
	return reduce(lambda set_, new: set_.union(new), sets)

VERSION = 1

class FileSystemState(object):
	def __init__(self, version=VERSION, known_paths=None):
		self.version = version
		self.known_paths = known_paths or {}
		self._zombies = {}
		self.lock = threading.RLock()

	def check(self):
		assert self.version == VERSION
	
	def __iter__(self):
		return iter(list(self.known_paths.keys()))

	def __len__(self):
		return len(self.known_paths)
	
	def items(self):
		return self.known_paths.items()

	def values(self):
		return self.known_paths.values()

	def __setitem__(self, item, value):
		with self.lock:
			log.debug("ALTERING path: %s" % (item,))
			assert isinstance(item, str)
			assert isinstance(value, FileState)
			self.known_paths[item] = value

	def __getitem__(self, item):
		with self.lock:
			return self.known_paths[item]

	def __delitem__(self, item):
		with self.lock:
			log.debug("DELETING known path: %s" % (item,))
			self._zombies[item] = self.known_paths[item]
			del self.known_paths[item]
	
	def resurrect(self, item):
		with self.lock:
			try:
				self.known_paths[item] = self._zombies[item]
				del self._zombies[item]
			except KeyError:
				return False
			return True

	
	def __repr__(self): return "\n" + "\n".join(map(repr, self.values()))
	def copy(self):
		cls, args = self.__reduce__()
		return cls(*args)

	def __reduce__(self):
		return (FileSystemState, (self.version, self.known_paths.copy()))


from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from watchdog import events
class QueueHandler(FileSystemEventHandler):
	def __init__(self):
		self.queue = queue.Queue()
	def dispatch(self, event):
		self.queue.put(event)


class FileSystemStateManager(object):
	def __init__(self, state = None):
		if state is None:
			state = FileSystemState()
		self.state = state
		self.anything_changed = threading.Event()
		self.lock = threading.Lock()
		self._event_handler = QueueHandler()
		self.reset()
	
	def reset(self):
		"""
		reset all diff-like attributes (changed, added, removed, etc)
		"""
		self.changed = set()
		self.added = set()
		self.removed = set()
		self.affected = set()

		self._seen = set()
		self.reset_scan()
		self.anything_changed.clear()

	def update(self):
		with self.lock:
			self.reset()
			self._walk(base)
			self._propagate_changes()

	def reset_scan(self):
		self._seen = set()
	
	def _init_filesystem_watch(self):
		observer = Observer()
		observer.schedule(self._event_handler, path='.', recursive=True)
		observer.start()

	def state_changes(self):
		self._process_events_thread = threading.Thread(target=self.process_events_forever, name="FileSystemState inotify event handler")
		self._process_events_thread.daemon = True
		self._process_events_thread.start()
		self._init_filesystem_watch()

		while True:
			self.anything_changed.wait()
			with self.lock:
				yield self
				self.reset()
	
	def process_events_forever(self):
		try:
			while(True):
				new_events = []
				new_events.append(self._event_handler.queue.get())
				# suck up the rest of the events while we're at it
				try:
					while True:
						new_events.append(self._event_handler.queue.get(False, timeout=0.1))
				except queue.Empty: pass
				self._process_changes(new_events)
		except:
			#TODO: should be able to kill the main thread here
			import traceback
			traceback.print_exc(file=sys.stderr)
			raise

	def _process_changes(self, changes):
		with self.lock:
			self.reset_scan()
			map(self._process_change, changes)
			self._propagate_changes()
			if self._all_differences():
				self.anything_changed.set()

	def _get_existing_and_nonexisting_paths(self, change):
		existing = []
		nonexisting = []
		if change.event_type == events.EVENT_TYPE_MOVED:
			existing.append(change.dest_path)
			nonexisting.append(change.src_path)
		elif change.event_type in (events.EVENT_TYPE_CREATED, events.EVENT_TYPE_MODIFIED):
			existing.append(change.src_path)
		elif change.event_type == events.EVENT_TYPE_DELETED:
			nonexisting.append(change.src_path)
		else:
			raise AssertionError("unknown event type: %s" % (change.event_type,))
		return existing, nonexisting

	def _process_change(self, change):
		existing, nonexisting = self._get_existing_and_nonexisting_paths(change)

		existing = filter(None, map(lambda path: file_util.relative(path, None), existing))
		nonexisting = filter(None, map(lambda path: file_util.relative(path, None), nonexisting))

		if len(existing + nonexisting) == 0:
			info("skipped: %s" % (change.src_path))
			return

		self.reset_scan()
		if not change.is_directory:
			existing = filter(file_util.is_pyfile, existing)
			nonexisting = filter(file_util.is_pyfile, nonexisting)
			map(self._inspect, existing)
			map(self._remove, nonexisting)

	@property
	def bad(self):
		return set([item.path for item in self.state.values() if not item.ok()])
	
	def __repr__(self):
		def _repr(attr):
			return "%s: %r" % (attr, getattr(self, attr))
		internals = ', '.join(map(_repr, ('changed','added','removed','state')))
		return '<%s: (%s)>' % (self.__class__.__name__,internals)
	
	def _all_differences(self):
		"""return all files that have been added, changed or deleted"""
		return union(self.changed, self.added, self.removed)
	
	def _propagate_changes(self):
		self.affected = self._all_differences()
		state_changed = True
		while state_changed:
			state_changed = False
			for path, state in self.state.items():
				if path in self.affected: # already changed; ignore
					continue
				if len(self.affected.intersection(state.dependencies)) > 0: # any item has changed
					info("affected: %s (depends on: %s)" % (
						path,
						", ".join(self.affected.intersection(state.dependencies))))
					self.affected.add(path)
					state_changed = True
		if len(self.affected) > 0:
			info("all affected files:    \n%s" % ("\n".join(["  %s" % (item,) for item in sorted(self.affected)]),))

	def _remove(self, path):
		info("removed: %s" % path)
		try:
			del self.state[path]
		except KeyError:
			pass
		self.removed.add(path)
	
	def _walk(self, dir):
		for root, dirs, files in os.walk(dir):
			for dir_ in dirs:
				if dir_.startswith('.'):
					dirs.remove(dir_)
			for file_ in files:
				try:
					rel_path = file_util.relative(os.path.join(root, file_))
				except file_util.FileOutsideCurrentRoot:
					info("skipped non-cwd file: %s" % (file_,))
					continue
				self._inspect(rel_path)

	def _inspect(self, rel_path):
		if not file_util.is_pyfile(rel_path):
			log.debug("ignoring non-python file: %s" % (rel_path,))
			return

		if rel_path in self._seen:
			debug("visited file twice: %s" % (rel_path))
			return
		self._seen.add(rel_path)

		with self.state.lock:
			if rel_path in self.state or self.state.resurrect(rel_path):
				self._check_for_change(rel_path)
			else:
				self._add(rel_path)
	
	def _add(self, rel_path):
		file_state = FileState(rel_path)
		info("added: %s" % (rel_path))
		self.added.add(rel_path)
		self.state[rel_path] = file_state
	
	def _check_for_change(self, rel_path):
		file_state = self.state[rel_path]
		if file_state.stale():
			info("changed: %s" % (rel_path,))
			file_state.update()
			self.changed.add(rel_path)
		else:
			debug("unchanged: %s" % (rel_path,))


