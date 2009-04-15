import os
import sys
import logging
import pickle

log = logging.getLogger(__name__)
debug = log.debug

from shared import FileStamp, file_util, const
import snakefood.find

CHANGED = 'changed'
AFFECTED = 'affected'
REMOVED = 'removed'
ADDED = 'added'
DEPENDENCIES = 'dependencies'

def load_dependencies(base=None):
	if base is None:
		base = const.cwd
	path = os.path.join(base, const.picklefile_name)
	try:
		picklefile = open(path)
		ret = pickle.load(picklefile)
		picklefile.close()
		debug("loaded: %s" % (picklefile.name,))
	except IOError:
		debug("IOError:", exc_info=sys.exc_info())
		ret = {}
	return ret

def save_dependencies(dependencies, base=None):
	if base is None:
		base = const.cwd
	picklefile = open(os.path.join(base, const.picklefile_name), 'w')
	pickle.dump(dependencies, picklefile)
	picklefile.close()
	debug("saved dependencies file: %s" % (picklefile.name))


class DependencyScanner(object):
	__in_progress = False
	base = const.cwd
	
	@staticmethod
	def _init_state(dependencies):
		return {
			CHANGED: set(),
			ADDED: set(),
			REMOVED: set(dependencies.keys()),
			DEPENDENCIES: dependencies,
		}
	
	def scan(self, dependencies={}):
		"""
		updates dependencies, and returns a dict with sets for each key in CHANGED, ADDED and REMOVED.
		each set is a set of most-recent filestamps
		"""
		state = self._init_state(dependencies)
		seen = set()
			
		for root, dirs, files in os.walk(self.base):
			for dir_ in dirs:
				if dir_.startswith('.'):
					dirs.remove(dir_)
			for file_ in files:
				rel_path = file_util.relative(os.path.join(root, file_))
				if rel_path is not None and file_util.is_pyfile(rel_path):
					self._scan_file(rel_path, state, seen)
				else:
					debug("skipped non-python or non-cwd file: %s" % (file_,))
		for removed_file in state[REMOVED]:
			debug("removed: %s" % removed_file)
		self._propagate_changes(state)
		return state
	
	def _propagate_changes(self, state):
		changes = state[AFFECTED] = set()
		changes.update(state[ADDED].union(state[CHANGED]).union(state[REMOVED]))
		dependencies = state[DEPENDENCIES]
		
		state_changed = True
		while state_changed:
			state_changed = False
			for key, items in dependencies.items():
				if key in changes: # already changed; ignore
					continue
				if len(changes.intersection(items)) > 0: # any item has changed
					state_changed = True
					changes.add(key)
		
	def _scan_file(self, rel_path, state, seen):
		if rel_path in seen:
			debug("visited file twice: %s" % (rel_path))
			return
		seen.add(rel_path)
		dependencies = state[DEPENDENCIES]
		if rel_path in state[REMOVED]:
			# nope, it's still here
			state[REMOVED].remove(rel_path)
			file_stamp = self._get_key_reference(dependencies, rel_path)
			debug(file_stamp)
			if file_stamp.stale():
				debug("updated: %s" % (rel_path,))
				file_stamp.update()
				state[CHANGED].add(file_stamp)
			else:
				debug("unchanged: %s" % (rel_path,))
		else:
			debug("added: %s" % (rel_path))
			file_stamp = FileStamp(rel_path)
			state[ADDED].add(file_stamp)
			dependencies[file_stamp] = self._get_dependencies(file_stamp)
	
	def _get_dependencies(self, file_stamp):
		paths = self._get_direct_dependency_paths(file_stamp.path)
		rel_paths = [FileStamp(file_util.relative(path)) for path in paths if file_util.relative(path) is not None]
		debug("rel_paths: %s" % (rel_paths))
		return rel_paths

	@staticmethod
	def _get_direct_dependency_paths(file_):
		debug("fetching dependencies for %s" % (file_,))
		files, errors = snakefood.find.find_dependencies(file_, verbose=False, process_pragmas=False)
		if len(errors) > 0:
			map(log.error, errors)
		debug("found dependant files: %s" % (files,))
		return files
	
	@staticmethod
	def _get_key_reference(dict_, key):
		keys = list(dict_.keys())
		if key not in dict_:
			raise ValueError("%s does not appear in keys of dict: %s" % (key, keys))
		return keys[keys.index(key)]


