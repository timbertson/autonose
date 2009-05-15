import test_helper

from mocktest import *
from sniffles.watcher import *
from sniffles import watcher as watcher_module

#TODO: fill in all these tests!

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
		environ = {'NOSE_SNIFFLES':True)
		parser = mock('parser')
		parser.expects('add_option').with(
			'--sniffles',
			action='store_true',
			default=True,
			dest='sniffles',
			help=anything)
		watcher.options(parser.raw, environ)

	def test_should_not_be_enabled_when_NOSE_SNIFFLES_is_set(self):
		watcher = Watcher()
		self.assertFalse(watcher.enabled)
		environ = {'NOSE_SNIFFLES':False)
		parser = mock('parser')
		parser.expects('add_option').with(
			'--sniffles',
			action='store_true',
			default=False,
			dest='sniffles',
			help=anything)
		watcher.options(parser.raw, environ)

	def test_should_scan_for_state_if_not_given_any(self):
		watcher = Watcher()
		state = mock('state')
		config = mock('config').with_children(sniffles=True)
		mock_on(watcher_module).scanner.expects('scan').once().returning(mock_state.raw)
		watcher.configure(config.raw)
	
	def test_should_only_run_affected_and_bad_files(self):
		watcher = Watcher()
		good = set([1,2,3])
		bad = set([4,5,6])
		changed = seet([7,8,9])
		state = mock('state').with_children(good=good, bad=bad, changed=changed)
		config = mock('config').with_children(sniffles=True)
		mock_on(watcher_module).scanner.expects('scan').once().returning(mock_state.raw)
		watcher.configure(config.raw)
		
		self.assertEqual(watcher.files_to_run, bad.union(good))

	def test_should_update_test_when_run(self):
		#TODO: deal with formatError & split these tests into 4
		good = mock('good')
		bad = mock('bad')
		ugly = mock('ugly')
		skippy = mock('skippy')
		watcher = Watcher()

		update_test = mock_on(watcher)._update_test
		update_test.is_expected.exactly(4).times
		
		update_test.is_expected.once()with_(good.raw, watcher_module.success)
		update_test.is_expected.once()with_(bad.raw, watcher_module.failure)
		update_test.is_expected.once()with_(ugly.raw, watcher_module.error)
		update_test.is_expected.once()with_(ugly.raw, watcher_module.skippy)
		
		watcher.beforeTest(good)
		watcher.addSuccess(good)
	
		watcher.beforeTest(bad)
		watcher.addFailure(bad)
	
		watcher.beforeTest(ugly)
		watcher.addError(ugly)

		watcher.beforeTest(skippy)
		watcher.afterTest(skippy)
	
	def test_should_update_test_forr_each_result_type(self):
		pass

	def test_should_save_state_on_finalize(self):
		state.expects('save').once()
		watcher.finalize()
		#??



