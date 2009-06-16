import test_helper

from mocktest import *
from autonose import scanner
import os, types

import __builtin__ as builtin

pickle_path = os.path.abspath('.autonose-depends.pickle')
class ScannerTest(TestCase):
	def test_should_load_saved_dependency_information(self):
		picklefile = mock('pickle file')
		mock_on(scanner).load.is_expected.\
			with_(pickle_path).\
			returning(picklefile.raw)
		pickle = mock('unpickled info')
		mock_on(scanner.pickle).load.is_expected.with_(picklefile).returning(pickle)
		
		loaded = scanner.load()
		self.assertEqual(loaded, pickle.raw)
		
	def test_should_print_a_useful_error_on_load_failure(self):
		import sys
		picklefile = mock('pickle file')
		mock_on(scanner.pickle).load.\
			is_expected.\
			raising(StandardError('oh noes'))
		mock_on(sys).stderr.expects('write').with_(string_matching("Failed loading \"\.autonose-depends\.pickle\"\. you may have to delete it\..*"))
		
		self.assertRaises(SystemExit, scanner.load, args=(1,))
	
	def test_should_save_dependency_information(self):
		picklefile = mock('pickle file')
		dependencies = mock('dependencies')
		state = mock('state').with_children(dependencies = dependencies.raw)
		mock_on(builtin).open.is_expected.with_(pickle_path, 'w').\
			returning(picklefile.raw)
		mock_on(scanner.pickle).dump.\
			is_expected.with_(dependencies.raw, picklefile.raw)
		picklefile.expects('close')
		print repr(state.raw.dependencies)
		scanner.save(state.raw)

	def test_should_scan_filesystem_for_updates(self):
		#TODO
		pass
	
	def test_should_delete_dependency_information_on_reset(self):
		
		mock_on(scanner.os.path).isfile.is_expected.with_(pickle_path).returning(True)
		mock_on(scanner.os).remove.is_expected.with_(pickle_path)
		scanner.reset()
	
	def test_should_only_delete_saved_dependencies_if_they_exist(self):
		mock_on(scanner.os.path).isfile.is_expected.with_(pickle_path).returning(False)
		mock_on(scanner.os).remove.is_not_expected
		scanner.reset()

