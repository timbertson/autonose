import os
import time
from unittest import TestCase

from sniffles.shared import FileStamp

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
	
	def test_should_not_equal_different_mtime(self):
		oldest = FileStamp(self.filename)
		self._touch()
		newest = FileStamp(self.filename)
		self.assertFalse(oldest == newest)
		self.assertTrue(oldest != newest)
	
	def test_should_order_by_mtime(self):
		oldest = FileStamp(self.filename)
		self._touch()
		newest = FileStamp(self.filename)
		self.assertTrue(oldest < newest)
		self.assertEqual([oldest, newest], sorted([newest, oldest]))
	
	def test_should_hash_by_path(self):
		stamp = FileStamp(self.filename)
		self.assertEqual(hash(stamp), hash(stamp.path))


