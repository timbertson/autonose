import os
import file_util
import logging
import snakefood.find
from test_result import TestResultSet

class FileState(object):
	def __init__(self, path):
		self._info = None
		self.path = path
		self.update()
	
	def __str__(self):
		return "%s@%s" % (self.path, self.modtime)

	def __repr__(self):
		return "<%s: %s, info:%r (depends on %s)>" % (self.__class__.__name__, self, self.info, len(self.dependencies))

	def _get_modtime(self):
		return os.stat(file_util.absolute(self.path)).st_mtime
	
	def stale(self):
		return self._get_modtime() != self.modtime
	
	def update(self):
		self.modtime = self._get_modtime()
		self.dependencies = self._get_dependencies()
		
	def _get_info(self):
		if self._info is None:
			self._info = TestResultSet()
		return self._info

	def _set_info(self, info):
		self._info = info
	info = property(_get_info, _set_info)
	
	def ok(self):
		return False if self._info is None else self._info.ok()
	
	def _get_dependencies(self):
		paths = self._get_direct_dependency_paths(self.path)
		rel_paths = filter(lambda x: x is not None, map(lambda p: file_util.relative(p, None), paths))
		logging.debug("rel_paths: %s" % (rel_paths))
		return rel_paths

	@staticmethod
	def _get_direct_dependency_paths(file_):
		logging.debug("fetching dependencies for %s" % (file_,))
		files, errors = snakefood.find.find_dependencies(file_, verbose=False, process_pragmas=False)
		if len(errors) > 0:
			map(logging.info, errors)
		logging.debug("found dependant files: %s" % (files,))
		return files

