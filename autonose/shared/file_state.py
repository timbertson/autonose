import os
import file_util
import logging
import snakefood.find
from test_result import TestResultSet
log = logging.getLogger(__name__)

class FileState(object):
	def __init__(self, path):
		self._test_results = None
		self.path = path
		self.update()
	
	def __str__(self):
		return "%s@%s" % (self.path, self.modtime)

	def __repr__(self):
		return "<%s: %s, test_results:%r (depends on %s files)>" % (self.__class__.__name__, self, self.test_results, len(self.dependencies))

	def _get_modtime(self):
		return os.stat(file_util.absolute(self.path)).st_mtime
	
	def stale(self):
		return self._get_modtime() != self.modtime
	
	def update(self):
		self.modtime = self._get_modtime()
		self.dependencies = self._get_dependencies()
		
	def _get_test_results(self):
		if self._test_results is None:
			self._test_results = TestResultSet()
		return self._test_results

	def _set_test_results(self, test_results):
		log.debug("added test_results %r to file state %s" % (test_results, self.path))
		self._test_results = test_results
	test_results = property(_get_test_results, _set_test_results)
	
	def ok(self):
		return False if self._test_results is None else self._test_results.ok()
	
	def _get_dependencies(self):
		paths = self._get_direct_dependency_paths(self.path)
		rel_paths = filter(lambda x: x is not None, map(lambda p: file_util.relative(p, None), paths))
		log.debug("rel_paths: %s" % (rel_paths))
		return rel_paths

	@staticmethod
	def _get_direct_dependency_paths(file_):
		log.debug("fetching dependencies for %s" % (file_,))
		files, errors = snakefood.find.find_dependencies(file_, verbose=False, process_pragmas=False)
		if len(errors) > 0:
			map(log.debug, errors)
		log.debug("found dependant files: %s" % (files,))
		return files

