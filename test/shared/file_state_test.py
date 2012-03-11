import os
import time
from unittest import TestCase, skip

from autonose.shared import FileState
from autonose.shared.test_result  import TestResultSet
from autonose.shared.test_result  import TestResult

class FileStateTest(TestCase):
	def setUp(self):
		self.filename = 'test.file'
		self._file = open(self.filename, 'w')
		self._file.write('contents!')
		self._file.close()

	def tearDown(self):
		os.remove(self._file.name)
	
	def test_should_get_current_modtime(self):
		mtime = os.stat(self.filename).st_mtime
		stamp = FileState(self.filename)
		
		self.assertEqual(stamp.path, self.filename)
		self.assertEqual(stamp.modtime, mtime)
	
	def _touch(self):
		newtime = time.time() + 10
		os.utime(self.filename, (newtime, newtime))
	
	def test_should_check_staleness(self):
		stamp = FileState(self.filename)
		self._touch()
		self.assertTrue(stamp.stale())

	def test_should_update_mtime(self):
		stamp = FileState(self.filename)
		self._touch()
		self.assertTrue(stamp.stale())
		stamp.update()
		self.assertFalse(stamp.stale())

	def test_should_default_to_new_test_result_set_info(self):
		self.assertEqual(FileState(self.filename).test_results, TestResultSet())
	
	@skip('TODO')
	def test_should_pickle(self):
		pass
	
	@skip('TODO')
	def test_should_remember_deleted_files_and_resurrect_them_if_they_reappear(self):
		pass

