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
	
	def _all_module_files(self, module_object):
		files = []
		try:
			files.append(module_object.__file__)
		except AttributeError: pass
		for key, value in module_object.__dict__.items():
			if not isinstance(value, types.ModuleType):
				continue
			try:
				files.append(value.__file__)
			except AttributeError: pass
		return files
			
	
	def _monitored_import(self, *args, **kwargs):
		mod = self._import(*args, **kwargs)
		if mod in [__builtin__, sys]:
			return mod
		try:
			fl = mod.__file__
		except AttributeError:
			log.error('module %r has no __file__ attribute' % (mod,))
			return mod
		if fl.startswith(self._base):
			files = self._all_module_files(mod)
			for mod_file in files:
				self._add_path(mod_file)
			self._add_path(fl)
				
		return mod

	def _insert_import(self):
		self._import = __builtin__.__import__
		__builtin__.__import__ = self._monitored_import

	def _revert_import(self):
		__builtin__.__import__ = self._import
	
	def path_for_module(self, name, module=None):
		if module is None:
			module = __import__(name)
		files = map(self._clean_filename, self._all_module_files(module))
		module_path = os.path.join(*str(name).split('.'))
		debug("files: %s" % files)
		debug("module_path: %s" % module_path)
		for file_ in files:
			if file_.startswith(module_path):
				return file_
		raise ValueError("module %s does not seem to have a canonical .py file in its top-level object files: %s" % (name, files))


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

		self.last_test = test
		debug('\n\ntest: ' + str(test.test.__module__))
		
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
				debug('depends on: ' + str(imported_file))
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

