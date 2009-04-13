import nose
import sys
import logging
import subprocess
import os
import re
import pickle
import types

from shared import FileStamp

log = logging.getLogger(__name__)
debug = log.debug
_cwd = os.path.realpath(os.getcwd())

import __builtin__

from shared.const import picklefile_name

def file_base(path):
	return remove_extension(os.path.basename(path))

def remove_extension(path):
	return path.rsplit('.', 1)[0]

def load_dependencies(base=None):
	if base is None:
		base = _cwd
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


class ImportMonitor(object):
	imported = []
	_pyc = re.compile('\.pyc', re.I)

	def __init__(self, base=None):
		if base is None:
			base = _cwd
		self._base = base
		self._insert_import()
	
	def end(self):
		self._revert_import()
		
	def reset(self):
		self.imported = []
	
	def _clean_filename(self, fname):
		if re.search(self._pyc, fname):
			fname = fname[:-1] # trim the 'c' from .pyc
		if fname.startswith(self._base):
			fname = fname[len(self._base)+1:]
		return fname
	
	def _add_path(self, path):
		real_path = self._clean_filename(path)
		if real_path not in self.imported:
			debug('imported: ' + str(real_path))
			self.imported.append(FileStamp(real_path))
	
	def _accumulate_all_module_files(self, accumulator_set, backtrack_set, module_object):
		"""
		for the given module and all sub-modules, add each module.__file__
		path to accumulator_set if they begin with self._base.
		
		note that child modules are traversed even if they do not
		reside within self._base
		
		backtrack_set is a set of already-seen files, to prevent infinite loops
		on circular references
		"""
		try:
			file_ = module_object.__file__
		except AttributeError:
			# debug("module %s has no __file__ attribute" % (module_object,))
			return
		if file_ in backtrack_set:
			return

		backtrack_set.add(file_)
		
		if file_.startswith(self._base):
			accumulator_set.add(file_)
		if os.path.basename(file_).startswith('__init__.'):
			for key, value in module_object.__dict__.items():
				if not isinstance(value, types.ModuleType):
					# debug("module.%s is not of type module" % (key,))
					continue
				self._accumulate_all_module_files(accumulator_set, backtrack_set, value)
	
	def _all_module_files(self, module_object):
		files = set()
		self._accumulate_all_module_files(files, set(), module_object)
		return files

	@classmethod
	def _ignore_non_parent_module_files(cls, module_name, module_files):
		possible_paths = cls._valid_parent_file_base_paths(module_name)
		files = []
		debug(possible_paths)
		debug(module_files)
		for file_ in module_files:
			file_base = remove_extension(file_)
			for module_path in possible_paths:
				if file_base.endswith(module_path):
					files.append(file_)
		return files
	
	def _monitored_import(self, *args, **kwargs):
		mod = self._import(*args, **kwargs)
		debug('importing: %s' % (args[0],))
		files = self._all_module_files(mod)
		debug('all files: %s' % (files))
		map(self._add_path, self._ignore_non_parent_module_files(args[0], files))
		return mod
	
	@staticmethod
	def _valid_parent_file_base_paths(module_name):
		"""
		return all possible parent path endings (minus extensions) for the given module name.
		e.g: given "some.test.module", possible parent file paths are:
		     - some/__init__
		     - some/test/__init__
		     - some/test/module
		     - some/test/module/__init__
		"""
		module_parts = module_name.split('.')
		path_endings = []
		previous_parts = []
		path_endings.append(os.path.join(*module_parts))
		for part in module_parts:
			previous_parts.append(part)
			path_endings.append(os.path.join(*(previous_parts + ['__init__'])))
		return path_endings

	def _insert_import(self):
		"""substitute the builtin import for our own"""
		self._import = __builtin__.__import__
		__builtin__.__import__ = self._monitored_import

	def _revert_import(self):
		"""remove our import from the call chain"""
		__builtin__.__import__ = self._import
	
	@staticmethod
	def _canonical_module_file(module_name, module_file_set):
		"""
		given a module name and file set, return the '.py' file the looks
		the most like it is the actual source file for that module
		"""
		module_path = os.path.join(*str(module_name).split('.'))
		for file_ in module_file_set:
			if (os.path.join(_cwd, file_)).rsplit('.', 1)[0].endswith(module_path):
				return file_
		raise ValueError("module %s does not seem to have a canonical .py file in its module tree: %s" % (module_name, module_file_set))
	
	def path_for_module(self, name, module=None):
		"""
		given a module name, find the single python
		file that defines that module
		"""
		if module is None:
			module = __import__(name)
		files = self._all_module_files(module)
		return self._canonical_module_file(name, files)


class Watcher(nose.plugins.Plugin):
	name = 'sniffles'
	score = 800

	def begin(self):
		self.file_dependencies = {}
		self.last_test = None
		self._importer = ImportMonitor()
		self.old_file_dependencies = load_dependencies()
			
	def beforeTest(self, test):
		if self.last_test is not None:
			self._afterTest()
			debug("-- END test.\n\n")

		self.last_test = test
		debug('** BEGIN test: ' + str(test.test.__module__))
		
	def _afterTest(self):
		test = self.last_test
		if test is None: return
		self.last_test = None

		modname = str(test.test.__module__)
		test_key = self._importer.path_for_module(modname)
		if not test_key in self.file_dependencies:
			self.file_dependencies[test_key] = []
		deps = self.file_dependencies[test_key]
		for imported_file in self._importer.imported:
			if imported_file.path not in deps:
				debug('%s depends on: %s' % (test_key, imported_file))
				deps.append(imported_file)
		
		self._importer.reset()
	
	def report(self, stream=None):
		self._afterTest()

		self._importer.end()
		self.old_file_dependencies.update(self.file_dependencies)
		debug(repr(self.file_dependencies))
		picklefile = open(os.path.join(_cwd, picklefile_name), 'w')
		pickle.dump(self.old_file_dependencies, picklefile)
		picklefile.close()
		debug("saved dependencies file: %s" % (picklefile.name))

