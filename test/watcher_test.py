import test_helper

from mocktest import *
from autonose.watcher import Watcher
from autonose import scanner
from autonose.shared.test_result import TestResult
from autonose.shared import test_result
from autonose import watcher as watcher_module

from autonose.shared import file_util
import time
import os

class WatcherTest(TestCase):
	def test_should_be_enabled_when_given___autonose_option(self):
		watcher = Watcher()
		self.assertFalse(watcher.enabled)
		config = mock('config').with_children(autonose=True)
		watcher.configure(config.raw)
		mock_on(watcher)._setup
		self.assertTrue(watcher.enabled)
	
	def test_should_be_enabled_when_AUTO_NOSE_is_set(self):
		watcher = Watcher()
		self.assertFalse(watcher.enabled)
		environ = {'AUTO_NOSE':True}
		parser = mock('parser')
		parser.expects('add_option').with_(
			'--autorun',
			action='store_true',
			default=True,
			dest='autonose',
			help=anything)
		watcher.options(parser.raw, environ)

	def test_should_not_be_enabled_when_AUTO_NOSE_is_not_set(self):
		watcher = Watcher()
		self.assertFalse(watcher.enabled)
		environ = {}
		parser = mock('parser')
		parser.expects('add_option').with_(
			'--autorun',
			action='store_true',
			default=False,
			dest='autonose',
			help=anything)
		watcher.options(parser.raw, environ)

	def test_should_scan_for_state_if_not_given_any(self):
		watcher = Watcher()
		state = mock('state').with_children(good=[],bad=[],affected=[])
		config = mock('config').with_children(autonose=True)
		mock_on(watcher_module.scanner).scan.is_expected.once().returning(state.raw)
		watcher_module.global_state = None
		watcher.configure(config.raw)
	
	def test_should_only_run_affected_and_bad_files(self):
		# have to use an object with a path for debugging purposes - not ideal..
		class Num(object):
			def __init__(self, n):
				self.n = n
				self.path = "PATH"
			def __repr__(self): return repr(self.n)
			def __str__(self):  return str(self.n)
			def __eq__(self, other): return self.n == other.n
		watcher = Watcher()
		watcher_module.global_state = None
		good = set(map(Num, [1,2,3]))
		bad = set(map(Num, [4,5,6]))
		changed = set(map(Num, [7,8,9]))
		affected = set(map(Num, [10,11,12]))
		state = mock('state').with_children(good=good, bad=bad, changed=changed, affected=affected)
		config = mock('config').with_children(autonose=True)
		mock_on(watcher_module).scanner.expects('scan').once().returning(state.raw)
		watcher.configure(config.raw)
		
		self.assertEqual(watcher.files_to_run, bad.union(affected))

	def test_should_update_test_on_success(self):
		watcher = Watcher()
		update_test = mock_on(watcher)._update_test

		good = mock('good')
		
		update_test.is_expected.once().with_(good.raw, test_result.success)
		watcher.beforeTest(good.raw)
		watcher.addSuccess(good.raw)

	def test_should_update_test_on_failure(self):
		watcher = Watcher()
		update_test = mock_on(watcher)._update_test

		bad = mock('bad').with_children(plugins=mock('bad plugins').with_methods(formatFailure=None).raw)
		bad_err = mock('bad_err')

		update_test.is_expected.once().with_(bad.raw, test_result.fail, bad_err.raw)

		watcher.beforeTest(bad.raw)
		watcher.handleFailure(bad.raw, bad_err.raw)

	def test_should_update_test_on_error(self):
		watcher = Watcher()
		update_test = mock_on(watcher)._update_test

		ugly = mock('ugly').with_children(plugins=mock('ugly plugins').with_methods(formatError=None).raw)
		ugly_err = mock('ugly_err')
		update_test.is_expected.once().with_(ugly.raw, test_result.error, ugly_err.raw)

		watcher.beforeTest(ugly.raw)
		watcher.handleError(ugly.raw, ugly_err.raw)

	def test_should_update_test_on_skip(self):
		watcher = Watcher()
		update_test = mock_on(watcher)._update_test

		skippy = mock('skippy')
		update_test.is_expected.once().with_(skippy.raw, test_result.skip)
		watcher.beforeTest(skippy.raw)
		watcher.afterTest(skippy.raw)
	
	def test_should_not_run_tests_from_outside_current_root(self):
		state = mock('state')
		path = mock('path')

		mock_on(file_util).relative.with_(path.raw).raising(file_util.FileOutsideCurrentRoot()).is_expected.once()
		
		watcher = Watcher(state.raw)

		self.assertEqual(watcher.wantFile(path.raw), False)
	
	def test_should_disregard_tests_from_outside_current_root(self):
		state = mock('state')
		path_ = mock('file')

		mock_on(file_util).relative.with_(path_.raw).raising(file_util.FileOutsideCurrentRoot()).is_expected.once()
		
		watcher = Watcher(state.raw)

		# should not affect state
		state.method('__getitem__').is_not_expected
		self.assertEqual(watcher.wantFile(path_.raw), False)
	
	def test_should_attach_test_results_to_files(self):
		start_time = 1234
		
		filesystem_state = mock('filesystem state').with_children(affected=[], bad=[])
		file_stamp = mock('file stamp')
		
		rel_path = 'relative source path.py'
		source_path = mock('source path')
		test_address = mock('address')

		new_test_result = mock('test result')
		test = mock('test').with_methods(address=[test_address.raw])
		test_state = mock('state')
		err = mock('err')
		
		watcher = Watcher(filesystem_state.raw)
		mock_on(time).time.returning(start_time)
		watcher._setup()

		mock_on(os.path).exists.returning(True)
		mock_on(file_util).source.returning(source_path.raw)
		mock_on(file_util).relative.with_(source_path.raw).returning(rel_path)
		
		mock_on(TestResult).__new__.is_expected.with_(any_(type), test_state.raw, test.raw, err.raw, start_time).returning(new_test_result.raw)
		filesystem_state.expects('__getitem__').with_(rel_path).returning(file_stamp.raw)
		file_stamp.child('info').expects('add').with_(new_test_result.raw)

		watcher._update_test(test.raw, test_state.raw, err.raw)

	def test_should_save_state_on_finalize(self):
		state = mock('filesystem state')
		watcher = Watcher(state.raw)

		mock_on(scanner).save.is_expected.once
		watcher.finalize()




