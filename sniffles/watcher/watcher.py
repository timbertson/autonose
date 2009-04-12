import nose
import sys
import logging
import subprocess
import os
import re
import pickle

log = logging.getLogger(__name__)
debug = log.debug
_cwd = os.path.realpath(os.getcwd())

import __builtin__

picklefile_name = '.sniffle-depends.pickle'

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
		
	def clear():
		self.imported = []
	
	def _clean_filename(self, fname):
		if re.search(self._pyc, fname):
			fname = fname[:-1] # trim the 'c' from .pyc
		if fname.startswith(self._base):
			fname = fname[len(self._base)+1:]
		return fname
	
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
			filestamp = FileStamp(self._clean_filename(fl))
			if filestamp not in self.imported:
				self.imported.append(filestamp)
		return mod

	def _insert_import(self):
		self._import = __builtin__.__import__
		__builtin__.__import__ = self._monitored_import

	def _revert_import(self):
		__builtin__.__import__ = self._import

class Watcher(nose.plugins.Plugin):
	name = 'sniffles'

	def begin(self):
		self.file_dependencies = {}
		self.last_test = None
		self._importer = ImportMonitor()
			
	def beforeTest(self, test):
		if self.last_test is not None:
			self._afterTest()

		self.last_test = test
		try:
			picklefile = open(os.path.join(_cwd, picklefile_name))
			self.old_file_dependencies = pickle.load(picklefile)
		except IOError:
			self.old_file_dependencies = {}
		
	def _afterTest(self):
		test = self.last_test
		if test is None: return
		self.last_test = None

		test_key = str(test.test.__module__)
		if not test_key in self.file_dependencies:
			self.file_dependencies[test_key] = set()
		deps = self.file_dependencies[test_key]
		deps.update(set(self._importer.imported))
	
	def report(self, stream=None):
		self._afterTest()

		self._importer.end()
		self.old_file_dependencies.update(self.file_dependencies)
		debug(repr(self.file_dependencies))
		picklefile = open(os.path.join(_cwd, picklefile_name), 'w')
		pickle.dump(self.old_file_dependencies, picklefile)
		picklefile.close()

class FileStamp(object):
	def __init__(self, path):
		self.path = path
		self.modtime = os.stat(os.path.join(_cwd, path)).st_mtime
	
	def __str__(self):
		return "%s@%s" % (self.path, self.modtime)

	def __repr__(self):
		return "#<%s: %s>" % (self.__class__.__name__, self)

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.path == other.path and self.modtime == other.modtime
		elif isinstance(other, str):
			return self.path == other



