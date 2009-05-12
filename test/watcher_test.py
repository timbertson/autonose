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
		
		mock_on(watcher_module).scanner.expects('scan').once().returning(mock_state.raw)
		#TODO
	
	def test_should_only_run_affected_and_bad_files(self):
		pass

	def test_should_update_test_when_run(self):
		pass
	
	def test_should_update_test_forr_each_result_type(self):
		pass

	def test_should_ensure_every_test_had_a_result(self):
		pass
	
	def test_should_save_state_on_finalize(self):
		pass



