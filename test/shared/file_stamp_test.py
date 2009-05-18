import os
import time
from unittest import TestCase

from autonose.shared import FileStamp
from autonose.shared.test_result  import TestResultSet

class FileStampTest(TestCase):
	def setUp(self):
		self.filename = 'test.file'
		self._file = open(self.filename, 'w')
		self._file.write('contents!')
		self._file.close()

	def tearDown(self):
		os.remove(self._file.name)
	
	def test_should_get_current_modtime(self):
		mtime = os.stat(self.filename).st_mtime
		stamp = FileStamp(self.filename)
		
		self.assertEqual(stamp.path, self.filename)
		self.assertEqual(stamp.modtime, mtime)
	
	def test_should_equal_path_string(self):
		stamp = FileStamp(self.filename)
		self.assertEqual(stamp, stamp.path)
		self.assertEqual(stamp.path, stamp)
	
	def _touch(self):
		newtime = time.time() + 10
		os.utime(self.filename, (newtime, newtime))
	
	def test_should_equal_filestamp_of_different_mtime(self):
		oldest = FileStamp(self.filename)
		self._touch()
		newest = FileStamp(self.filename)
		self.assertTrue(oldest == newest)
		self.assertFalse(oldest != newest)
	
	def test_should_hash_by_path(self):
		stamp = FileStamp(self.filename)
		self.assertEqual(hash(stamp), hash(stamp.path))
	
	def test_should_check_staleness(self):
		stamp = FileStamp(self.filename)
		self._touch()
		self.assertTrue(stamp.stale())

	def test_should_update_mtime(self):
		stamp = FileStamp(self.filename)
		self._touch()
		self.assertTrue(stamp.stale())
		stamp.update()
		self.assertFalse(stamp.stale())

	def test_should_default_to_new_test_result_set_info(self):
		self.assertEqual(FileStamp(self.filename).info, TestResultSet())

