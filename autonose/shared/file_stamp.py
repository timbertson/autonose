import os
import file_util
from test_result import TestResultSet
from const import cwd

class FileStamp(object):
	_info = None
	def __init__(self, path):
		self.path = path
		self.modtime = self._get_modtime()
	
	def __str__(self):
		return "%s@%s" % (self.path, self.modtime)

	def __repr__(self):
		return "<%s: %s, info:%r>" % (self.__class__.__name__, self, self.info)

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.path == other.path
		elif isinstance(other, str):
			return self.path == other
	
	def __ne__(self, other):
		return not self == other
	
	def __hash__(self):
		return hash(self.path)

	def __cmp__(self, other):
		return cmp(self.path, other.path)
	
	def _get_modtime(self):
		print os
		return os.stat(file_util.absolute(self.path)).st_mtime
	
	def stale(self):
		return self._get_modtime() != self.modtime
	
	def update(self):
		self.modtime = self._get_modtime()
		
	def _get_info(self):
		if self._info is None:
			self._info = TestResultSet()
		return self._info

	def _set_info(self, info):
		self._info = info
	info = property(_get_info, _set_info)
	
	def ok(self):
		return False if self._info is None else self._info.ok()
	


