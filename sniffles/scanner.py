import os
import logging

log = logging.getLogger(__name__)
debug = log.debug

from shared import FileStamp

class FSChanges(object):
	__in_progress = False
	def __init__(self, base_path, current_stamps):
		self.base = base_path
		self.stamps = current_stamps
	
	def scan(self, current_stamps=None):
		if self.__in_progress:
			raise RuntimeError("%s can't run multiple concurrent scans" % (self.__class__.__name__,))
		self.__in_progress = True
		if current_stamps is not None:
			self.stamps = current_stamps
		self._updated = []
		self._added = []
		self._removed = self.stamps
		
		for root, dirs, files in os.walk(self.base):
			for dir_ in dirs:
				if dir_.startswith('.'):
					dirs.remove(dir_)
			for file_ in files:
				full_path = os.path.join(root, file_)
				self._scan_file(full_path)
		for removed_file in self._removed:
			debug("removed: %s" % removed_file)
		self.__in_progress = False
		
	def _scan_file(self, full_path):
		rel_path = full_path[len(self.base)+1:]
		current_filestamp = FileStamp(rel_path)
		if rel_path in self.stamps:
			if rel_path in self._removed:
				self._removed.remove(rel_path)
			if current_filestamp != self.deps[rel_path]:
				debug("updated: %s" % (rel_path,))
				self._updated.apend(current_filestamp)
			else:
				debug("unchanged: %s" % (rel_path,))
		else:
			debug("added: %s" % (rel_path))
			self._added.append(current_filestamp)

