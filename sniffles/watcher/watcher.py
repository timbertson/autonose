import nose
import sys
import logging
import subprocess
import os
import pickle

from ..shared.const import cwd
from ..shared.const import picklefile_name

from import_monitor import ImportMonitor

log = logging.getLogger(__name__)
debug = log.debug

__all__ = ['load_dependencies', 'Watcher']

def load_dependencies(base=None):
	if base is None:
		base = cwd
	path = os.path.join(base, picklefile_name)
	try:
		picklefile = open(path)
		ret = pickle.load(picklefile)
		picklefile.close()
		debug("loaded: %s" % (picklefile.name,))
	except IOError:
		debug("IOError: (cwd=%s)", os.getcwd(), exc_info=sys.exc_info())
		ret = {}
	return ret

#FIXME: hooking _importer at self.before() causes *all* test files to be depended upon by the
# first test, since nose imports the test modules before tests are run.

class Watcher(nose.plugins.Plugin):
	name = 'sniffles'
	score = 800

	def begin(self):
		self.file_dependencies = {}
		self.last_test = None
		self._importer = ImportMonitor()
		self.old_file_dependencies = load_dependencies()
	
	def beforeImport(self, *args):
		self._importer.start()
		debug("-- import test: %s" % (args,))
		
	def beforeTest(self, test):
		if self.last_test is not None:
			self._afterTest()
			debug("-- END test.\n\n")

		self.last_test = test
		self._importer.start()
		debug('** BEGIN test:  %s' % str(test.test))
		# import this now, to ensure it is caught by our import listener
		__import__(str(test.test.__module__))
		
	def _afterTest(self):
		test = self.last_test
		if test is None: return
		self.last_test = None
		self._importer.reset()
		self._importer.stop()

		modname = str(test.test.__module__)
		test_key = self._importer.path_for_module(modname)
		if not test_key in self.file_dependencies:
			self.file_dependencies[test_key] = []
		deps = self.file_dependencies[test_key]
		for imported_file in self._importer.imported:
			if imported_file.path not in deps:
				debug('%s depends on: %s' % (test_key, imported_file))
				deps.append(imported_file)
		debug('*** - dependant files for %s: %s' % (test_key, deps,))
	
	def report(self, stream=None):
		self._afterTest()

		self._importer.stop()
		self.old_file_dependencies.update(self.file_dependencies)
		debug(repr(self.file_dependencies))
		picklefile = open(os.path.join(cwd, picklefile_name), 'w')
		pickle.dump(self.old_file_dependencies, picklefile)
		picklefile.close()
		debug("saved dependencies file: %s" % (picklefile.name))

