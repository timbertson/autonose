import test_helper

from mocktest import *
from autotest import scanner

class ScannerTest(TestCase):
	def test_should_load_saved_dependency_information(self):
			with_('.autonose-depends.pickle').\
		picklefile = mock('pickle file')
		mock_on(scanner).load.is_expected.\
			returning(picklefile.raw)
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
	
	def test_should_save_dependency_information(self):
		picklefile = mock('pickle file')
		state = mock('state')
		mock_on(scanner).open.is_expected.with_('.autonose-depends.pickle').\
			returning(picklefile)
		mock_on(scanner.pickle).dump.\
			is_expected.with_(picklefile, state)
		picklefile.expects('close')
		
		scanner.save(state)

	def test_should_scan_filesystem_for_updates(self):
		#TODO
		pass

