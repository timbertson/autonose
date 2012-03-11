import test_helper

import logging
from mocktest import *
from autonose import scanner
import os, types
import sys

pickle_path = os.path.abspath('.autonose-depends.pickle')
class ScannerTest(TestCase):
	def test_should_load_saved_dependency_information(self):
		picklefile = mock('pickle file')
		expect(scanner).open_file(pickle_path).and_return(picklefile)
		pickle = mock('unpickled info')
		expect(scanner.pickle).load(picklefile).and_return(pickle)

		manager = mock('manager')
		expect(scanner.FileSystemStateManager)['__new__'](any_(type), pickle).and_return(manager)
		
		loaded = scanner.load()
		self.assertEqual(loaded, manager)
		
	def test_should_print_a_useful_error_on_load_failure_when_pickle_exists(self):
		picklefile = mock('pickle file')
		f = open(pickle_path, 'w')
		f.write('garbage')
		f.close()
		modify(sys).stderr = mock('stderr')
		expect(sys.stderr).write(string_matching("Failed loading \"\.autonose-depends\.pickle\"\."))
		expect(sys.stderr).write("Deleting picklefile and trying again...")
		expect(sys.stderr).write('\n')
		expect(os).remove(pickle_path)
		logger = logging.getLogger("autonose.scanner")
		try:
			logger.setLevel(logging.CRITICAL)
			self.assertRaises(SystemExit, scanner.load, args=(1,))
		finally:
			logger.setLevel(logging.ERROR)
			try:
				os.remove(pickle_path)
			except OSError: pass
	
	def test_should_return_an_empty_dict_when_no_pickle_exists(self):
		expect(scanner).open_file.and_raise(IOError())
		state = mock('state')
		manager = mock('manager')
		expect(scanner.FileSystemState)['__new__'].and_return(state)
		expect(scanner.FileSystemStateManager)['__new__'].and_return(manager)
		expect(scanner.pickle).load.never()
		expect(manager).update
		modify(sys).stderr = mock('stderr')
		expect(sys.stderr).write.never()
		
		self.assertEqual(scanner.load(), manager)
	
	def test_should_delete_dependency_information_on_reset(self):
		expect(scanner.os.path).exists(pickle_path).and_return(True)
		expect(scanner.os).remove(pickle_path)
		scanner.reset()
	
	def test_should_only_delete_saved_dependencies_if_they_exist(self):
		expect(scanner.os.path).exists(pickle_path).and_return(False)
		expect(scanner.os).remove.never()
		scanner.reset()

