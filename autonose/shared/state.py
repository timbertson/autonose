import os
import logging

import snakefood.find

from file_stamp import FileStamp
import file_util
from const import cwd as base

log = logging.getLogger(__name__)
debug = log.debug
info = logging.getLogger(__name__ + '.summary').info

# TODO: shut up about unfound imports
#logging.getLogger(snakefood.find.logname).setLevel(logging.ERROR)

def get_path(item): return item.path

def union(*sets):
	return reduce(lambda set_, new: set_.union(new), sets)

class FileSystemState(object):
	def __init__(self, dependencies = {}):
		self.dependencies = dependencies
		self.reset()
	
	def reset(self, dependencies = None):
		"""
		reset all diff-like attributes (changed, added, removed, etc)
		"""
		if dependencies is not None:
			self.dependencies = dependencies
		self.changed = set()
		self.added = set()
		self.removed = set()

		self._affected = None
		self._seen = set()
	
	def _get_affected(self):
		if self._affected is None:
			self._propagate_changes()
		return self._affected
	affected = property(_get_affected)

	def _get_bad(self):
		return set(filter(lambda item: item.info.ok() is False, self.dependencies.keys()))
	bad = property(_get_bad)
	
	def __repr__(self):
		def _repr(attr):
			return "%s: %r" % (attr, getattr(self, attr))
		internals = ', '.join(map(_repr, ('changed','added','removed','dependencies')))
		return '<%s: (%s)>' % (self.__class__.__name__,internals)
	
	def _all_differences(self):
		"""return all files that have been added, changed or deleted"""
		return union(self.changed, self.added, self.removed)
	
	def _propagate_changes(self):
		self._affected = self._all_differences()
		state_changed = True
		while state_changed:
			state_changed = False
			for key, values in self.dependencies.items():
				if key in self._affected: # already changed; ignore
					continue
				if len(self._affected.intersection(values)) > 0: # any item has changed
					info("affected: %s (depends on: %s)" % (
						get_path(key),
						", ".join(map(get_path, self._affected.intersection(values)))))
					self._affected.add(key)
					state_changed = True
		if len(self._affected) > 0:
			info("all affected files:    \n%s" % ("\n".join(["  %s" % (get_path(item),) for item in sorted(self._affected)]),))

	def anything_changed(self):
		return sum(map(len, (self.changed, self.added, self.removed))) > 0
	
	def update(self):
		"""
		updates state by visiting all python files in `base`
		"""
		self.reset()
		self.removed = set(self.dependencies)
		for root, dirs, files in os.walk(base):
			for dir_ in dirs:
				if dir_.startswith('.'):
					dirs.remove(dir_)
			for file_ in files:
				rel_path = file_util.relative(os.path.join(root, file_), None)
				if rel_path is not None and file_util.is_pyfile(rel_path):
					self.inspect(rel_path, known_exists = True)
				else:
					debug("skipped non-python or non-cwd file: %s" % (file_,))
		for removed_file in self.removed:
			info("removed: %s" % removed_file.path)
			del self.dependencies[removed_file.path]

	def inspect(self, rel_path, known_exists = False):
		if rel_path in self._seen:
			debug("visited file twice: %s" % (rel_path))
			return
		self._seen.add(rel_path)

		exists = (True if known_exists
			else os.path.exists(os.path.join(base, rel_path)))

		if rel_path in self.removed and exists:
			self.removed.remove(rel_path) # it still exists!
		
		if rel_path in self.dependencies:
			self._check_for_change(rel_path)
		else:
			self._add(rel_path)
	
	def _add(self, rel_path):
		info("added: %s" % (rel_path))
		file_stamp = FileStamp(rel_path)
		self.added.add(file_stamp)
		self.dependencies[file_stamp] = self._get_dependencies(file_stamp)
	
	def _check_for_change(self, rel_path):
		file_stamp = self._get_key_reference(self.dependencies, rel_path)
		debug(file_stamp)
		if file_stamp.stale():
			info("changed: %s" % (rel_path,))
			file_stamp.update()
			self.changed.add(file_stamp)
		else:
			debug("unchanged: %s" % (rel_path,))

	def _get_dependencies(self, file_stamp):
		paths = self._get_direct_dependency_paths(file_stamp.path)
		rel_paths = [FileStamp(file_util.relative(path)) for path in paths if file_util.relative(path, None) is not None]
		debug("rel_paths: %s" % (rel_paths))
		return rel_paths

	@staticmethod
	def _get_direct_dependency_paths(file_):
		debug("fetching dependencies for %s" % (file_,))
		files, errors = snakefood.find.find_dependencies(file_, verbose=False, process_pragmas=False)
		if len(errors) > 0:
			map(log.info, errors)
		debug("found dependant files: %s" % (files,))
		return files
	
	def __getitem__(self, name):
		return self._get_key_reference(self.dependencies, name)
	
	@staticmethod
	def _get_key_reference(dict_, key):
		keys = list(dict_.keys())
		if key not in dict_:
			raise ValueError("%s does not appear in keys of dict: %s" % (key, keys))
		return keys[keys.index(key)]


