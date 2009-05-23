import test_helper

from mocktest import *
from autotest import scanner

#TODO: fill in all these tests!

class ScannerTest(TestCase):
	def test_should_load_saved_dependency_information(self):
		picklefile = mock('pickle file')
		mock_on(scanner).load.is_expected.with('.autonose-depends.pickle').returning(picklefile.raw)
		pickle = mock('unpickled info')
		mock_on(scanner.pickle).load.is_expected.with_(picklefile).returning(pickle)
		
		loaded = scanner.load()
		self.assertEqual(loaded, pickle.raw)
		
	def test_should_print_a_useful_error_on_load_failure(self):
		import sys
		picklefile = mock('pickle file')
		mock_on(scanner).load.is_expected.with('.autonose-depends.pickle').returning(picklefile.raw)
		
		mock_on(scanner.pickle).load.\
			is_expected.with('.autonose-depends.pickle').\
			raising(StandardError('oh noes'))
		mock_on(sys).stderr.expects('write').with('xxx')
		
		self.assertRaises(scanner.load, SystemExit(1))
		#TODO
	
	def test_should_save_dependency_information(self):
		pass

	def test_should_scan_filesystem_for_updates(self):
		pass

