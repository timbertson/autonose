import os
import re
import __builtin__
import logging

from ..shared.const import cwd
from ..shared import FileStamp
import module_tools

log = logging.getLogger(__name__)
debug = log.debug


class ImportMonitor(object):
	imported = []
	_pyc = re.compile('\.pyc', re.I)
	_active = False

	def __init__(self, base=None):
		if base is None:
			base = cwd
		self._base = base
		self.reset()
	
	def start(self):
		self._insert_import()
		
	def stop(self):
		self._revert_import()
		
	def reset(self):
		debug("%r :: reset()" % (self))
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
	
	def _within_base(self, path):
		return path.startswith(self._base)

	def _monitored_import(self, *args, **kwargs):
		mod = self._import(*args, **kwargs)
		debug('importing: %s' % (args[0],))
		files = filter(self._within_base, module_tools.all_parent_module_files(args[0], mod))
		if len(files) > 0:
			debug('         : %s' % (files))
		map(self._add_path, files)
		return mod

	def _insert_import(self):
		"""substitute the builtin import for our own"""
		if self._active: return
		self._import = __builtin__.__import__
		__builtin__.__import__ = self._monitored_import
		self._active = True

	def _revert_import(self):
		if not self._active: return
		"""remove our import from the call chain"""
		__builtin__.__import__ = self._import
	
	def path_for_module(self, name, module=None):
		"""
		given a module name, find the single python
		file that defines that module
		"""
		if module is None:
			module = __import__(name)
		files = module_tools.all_module_files(module)
		return self._clean_filename(module_tools.canonical_module_file(name, files))

