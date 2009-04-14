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
		self._importer = ImportMonitor()
		self.old_file_dependencies = load_dependencies()
	
	def beforeImport(self, filename, module):
		self._importer.start()
		debug("-- BEFORE import test: %s" % ((filename, module),))
	
	def afterImport(self, filename, module):
		debug("-- AFTER import test: %s" % ((filename, module),))
		self._importer.stop()
		if os.path.isfile(os.path.realpath(filename)):
			self._attribute_imports_to_module_named(module)
		else:
			debug("adding test module without .py file: %s" % (module,))
			init_path = os.path.realpath(os.path.join(filename, '__init__.py'))
			if os.path.isfile(init_path):
				self._attribute_imports_to_key(self._importer.clean_path(init_path))
			else:
				raise RuntimeError("path is not a .py file nor a directory containing an __init__.py file: %s"  % (filename,))
	
	def _get_file_dependencies(self, key):
		if not key in self.file_dependencies:
			self.file_dependencies[key] = []
		return self.file_dependencies[key]
	
	def _attribute_imports_to_key(self, key):
		if len(self._importer.imported) > 0:
			debug("attributing imports to key: %s" % (key,))
		deps = self._get_file_dependencies(key)
		for imported_file in self._importer.imported:
			if imported_file.path not in deps:
				debug('%s depends on: %s' % (key, imported_file))
				deps.append(imported_file)
		self._importer.reset()
		return deps

	def _attribute_imports_to_module_named(self, module_name):
		test_key = self._importer.path_for_module(module_name)
		return self._attribute_imports_to_key(test_key)
		
	def beforeTest(self, test):
		self._importer.start()
		debug('** BEGIN test:  %s' % str(test.test))
		# import this now, to ensure it is caught by our import listener
		# TODO: can this be removed?
		__import__(str(test.test.__module__))
		
	def afterTest(self, test):
		debug("-- END test.\n\n")
		self._importer.stop()

		modname = str(test.test.__module__)
		deps = self._attribute_imports_to_module_named(modname)
		self._expand_dependencies(deps)
		debug('*** - dependant files for %s: %s' % (modname, deps,))
	
	def _expand_dependencies(self, deps):
		for dep in deps:
			if dep.path in self.file_dependencies:
				child_dependencies = self.file_dependencies[dep.path]
				for child_dep in child_dependencies:
					if child_dep.path not in deps:
						deps.append(child_dep)
	
	def report(self, stream=None):
		self._importer.stop()
		self.old_file_dependencies.update(self.file_dependencies)
		debug(repr(self.file_dependencies))
		picklefile = open(os.path.join(cwd, picklefile_name), 'w')
		pickle.dump(self.old_file_dependencies, picklefile)
		picklefile.close()
		debug("saved dependencies file: %s" % (picklefile.name))

	#TODO: this shouldn't be necessary (along with the rest of this file):
	def prepareTestLoader(self, loader):
		return LazyTestLoader(loader)

from inspect import isfunction, ismethod
from nose.util import cmp_lineno, isclass
from nose.suite import ContextList, LazySuite

class LazyTestLoader(nose.loader.TestLoader):
	def __init__(self, delegate):
		# emulate the original loader as much as we can
		super(self.__class__, self).__init__(
			config=delegate.config,
			importer=delegate.importer,
			workingDir=delegate.workingDir,
			selector=delegate.selector)
	
	def loadTestsFromModule(self, module, discovered):
		"""Load all tests from module and return a suite containing
		them. If the module has been discovered and is not test-like,
		the suite will be empty by default, though plugins may add
		their own tests.
		"""
		return LazySuite(lambda: self._lazyLoadTestsFromModule(module, discovered))
		
	def _lazyLoadTestsFromModule(self, module, discovered):
		# copied verbatim from nosetests v0.10.3 (loader.py);
		# modified to yield tests instead of returning all in one big list
		# added/removed lines marked with #TJC (+/-)
		log.debug("Load from module %s", module)
		tests = []
		test_classes = []
		test_funcs = []
		# For *discovered* modules, we only load tests when the module looks
		# testlike. For modules we've been directed to load, we always
		# look for tests. (discovered is set to True by loadTestsFromDir)
		if not discovered or self.selector.wantModule(module):
			for item in dir(module):
				test = getattr(module, item, None)
				# print "Check %s (%s) in %s" % (item, test, module.__name__)
				if isclass(test):
					if self.selector.wantClass(test):
						test_classes.append(test)
				elif isfunction(test) and self.selector.wantFunction(test):
					test_funcs.append(test)
			test_classes.sort(lambda a, b: cmp(a.__name__, b.__name__))
			test_funcs.sort(cmp_lineno)
			tests = map(lambda t: self.makeTest(t, parent=module),
						test_classes + test_funcs)
			yield self.suiteClass(ContextList(tests, context=module)) #TJC +
			tests = [] #TJC +

		# Now, descend into packages
		# FIXME can or should this be lazy?
		# is this syntax 2.2 compatible?
		paths = getattr(module, '__path__', [])
		for path in paths:
			# tests.extend(self.loadTestsFromDir(path))  #TJC -
			debug("yielding tests from dir: %s" % (path))
			yield self.suiteClass(                       #TJC +
				lambda: self.loadTestsFromDir(path))     #TJC +
			
		for test in self.config.plugins.loadTestsFromModule(module):
			# tests.append(test) #TJC -
			yield test           #TJC +

