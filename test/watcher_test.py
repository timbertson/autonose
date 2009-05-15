import test_helper

from mocktest import *
from sniffles.watcher import Watcher
from sniffles import scanner
from sniffles.shared.test_result import TestResult
from sniffles.shared import test_result
from sniffles import watcher as watcher_module

from sniffles.shared import file_util
import time
import os


#TODO: move this matcher stuff into mocktest
def matcher(matches, desc):
	return type('Matcher', (Matcher,), {'matches':matches, 'desc': lambda self: desc})()

class Matcher(object):
	_desc = 'anonymous matcher'

	def desc(self):
		return self._desc

	def __eq__(self, other):
		return self.matches(other)
	
	def __call__(self, *args):
		self.params = args
	
	def __str__(self):
		return "Matcher for \"%s\"" % (self.desc(),)

	def __repr__(self):
		return "<#Matcher: %s>" % (self.desc(),)

anything = matcher(lambda self, other: True, lambda self: 'any object')

class WatcherTest(TestCase):
	def test_should_be_enabled_when_given___sniffles_option(self):
		watcher = Watcher()
		self.assertFalse(watcher.enabled)
		config = mock('config').with_children(sniffles=True)
		watcher.configure(config.raw)
		mock_on(watcher)._setup
		self.assertTrue(watcher.enabled)
	
	def test_should_be_enabled_when_NOSE_SNIFFLES_is_set(self):
		watcher = Watcher()
		self.assertFalse(watcher.enabled)
		environ = {'NOSE_SNIFFLES':True}
		parser = mock('parser')
		parser.expects('add_option').with_(
			'--sniffles',
			action='store_true',
			default=True,
			dest='sniffles',
			help=anything)
		watcher.options(parser.raw, environ)

	def test_should_not_be_enabled_when_NOSE_SNIFFLES_is_set(self):
		watcher = Watcher()
		self.assertFalse(watcher.enabled)
		environ = {'NOSE_SNIFFLES':False}
		parser = mock('parser')
		parser.expects('add_option').with_(
			'--sniffles',
			action='store_true',
			default=False,
			dest='sniffles',
			help=anything)
		watcher.options(parser.raw, environ)

	def test_should_scan_for_state_if_not_given_any(self):
		watcher = Watcher()
		state = mock('state').with_children(good=[],bad=[],affected=[])
		config = mock('config').with_children(sniffles=True)
		mock_on(watcher_module).scanner.expects('scan').once().returning(state.raw)
		watcher.configure(config.raw)
	
	def test_should_only_run_affected_and_bad_files(self):
		watcher = Watcher()
		good = set([1,2,3])
		bad = set([4,5,6])
		changed = set([7,8,9])
		affected = set([10,11,12])
		state = mock('state').with_children(good=good, bad=bad, changed=changed, affected=affected)
		config = mock('config').with_children(sniffles=True)
		mock_on(watcher_module).scanner.expects('scan').once().returning(state.raw)
		watcher.configure(config.raw)
		
		self.assertEqual(watcher.files_to_run, bad.union(affected))

	def test_should_update_test_when_run(self):
		#TODO: deal with formatError & split these tests into 4
		good = mock('good')
		bad = mock('bad').with_children(plugins=mock('bad plugins').with_methods(formatFailure=None).raw)
		bad_err = mock('bad_err')
		ugly = mock('ugly').with_children(plugins=mock('ugly plugins').with_methods(formatError=None).raw)
		ugly_err = mock('ugly_err')
		skippy = mock('skippy')
		watcher = Watcher()
		
		update_test = mock_on(watcher)._update_test
		update_test.is_expected.exactly(4).times
		
		update_test.is_expected.once().with_(good.raw, test_result.success)
		update_test.is_expected.once().with_(bad.raw, test_result.fail, bad_err.raw)
		update_test.is_expected.once().with_(ugly.raw, test_result.error, ugly_err.raw)
		update_test.is_expected.once().with_(skippy.raw, test_result.skip)
		
		watcher.beforeTest(good.raw)
		watcher.addSuccess(good.raw)
	
		watcher.beforeTest(bad.raw)
		watcher.addFailure(bad.raw, bad_err.raw)
	
		watcher.beforeTest(ugly.raw)
		watcher.addError(ugly.raw, ugly_err.raw)

		watcher.beforeTest(skippy.raw)
		watcher.afterTest(skippy.raw)
	
	def test_should_not_run_tests_from_outside_current_root(self):
		state = mock('state')
		path = mock('path')

		mock_on(file_util).relative.with_(path.raw).raising(file_util.FileOutsideCurrentRoot()).is_expected.once()
		
		watcher = Watcher(state.raw)

		self.assertEqual(watcher.wantFile(path.raw), False)
	
	@ignore("awaiting mocktest support for __getitem__")
	def test_should_disregard_tests_from_outside_current_root(self):
		state = mock('state')
		path_ = mock('file')

		mock_on(file_util).relative.with_(path_.raw).raising(file_util.FileOutsideCurrentRoot()).is_expected.once()
		
		watcher = Watcher(state.raw)

		# should not affect state
		state.method('__getitem__').is_not_expected
		self.assertEqual(watcher.wantFile(path.raw), False)
	
	@ignore("awaiting mocktest support for is_not_expected")
	def test_should_attach_test_results_to_files(self):
		start_time = 1234
		
		filesystem_state = mock('filesystem state').with_children(affected=[], bad=[])
		file_stamp = mock('file stamp')
		
		rel_path = mock('relative source path')
		source_path = mock('source path')
		test_address = mock('address')

		new_test_result = mock('test result')
		test = mock('test').with_children(address=[test_address.raw])
		test_state = mock('state')
		err = mock('err')
		
		watcher = Watcher(filesystem_state.raw)
		mock_on(time).time.returning(start_time)
		watcher._setup()

		mock_on(os.path).exists.returning(True)
		mock_on(file_util).source.with_(test_address).returning(source_path.raw)
		mock_on(file_util).relative.with_(source_path.raw).returning(rel_path.raw)
		
		mock_on(TestResult).__new__.is_expected.with_(test_state.raw, test.raw, err.raw, start_time).returning(new_test_result.raw)
		filesystem_state.expects('__getitem__').with_(rel_path).returning(file_stamp.raw)
		file_stamp.child('info').expects('add').with_(new_test_result.raw)

		watcher._update_test(test.raw, state.raw, err.raw)

	def test_should_save_state_on_finalize(self):
		state = mock('filesystem state')
		watcher = Watcher(state.raw)

		mock_on(scanner).save.is_expected.once
		watcher.finalize()




