from . import test_helper

from mocktest import *
from autonose.watcher import Watcher
from autonose import scanner
from autonose.shared.test_result import TestResult
from autonose.shared import test_result
from autonose import watcher as watcher_module
from unittest import skip

from autonose.shared import file_util
import time
import os

import logging
def without_logging(func, level=logging.WARNING):
	log = logging.disable(level)
	try:
		func()
	finally:
		log = logging.disable(logging.NOTSET)

#@skip('TODO: requires updating, state_manager is used instead of scanning directly')
class WatcherTest(TestCase):
	def watcher(self, state_manager=None):
		def default_manager():
			manager = mock('state manager').with_children(bad=[], affected=[])
			return manager
		self.state_manager = state_manager or default_manager()
		return Watcher(self.state_manager)

	def test_should_only_run_affected_and_bad_files(self):
		# have to use an object with a path for debugging purposes - not ideal..
		class Num(object):
			def __init__(self, n):
				self.n = n
				self.path = "PATH"
			def __repr__(self): return repr(self.n)
			def __str__(self):  return str(self.n)
			def __eq__(self, other): return self.n == other.n
		good = set(map(Num, [1,2,3]))
		bad = set(map(Num, [4,5,6]))
		changed = set(map(Num, [7,8,9]))
		affected = set(map(Num, [10,11,12]))
		state = mock('state').with_children(good=good, bad=bad, changed=changed, affected=affected)
		watcher = self.watcher(state)
		
		self.assertEqual(watcher.files_to_run, bad.union(affected))

	def test_should_update_test_on_success(self):
		watcher = self.watcher()
		good = mock('good')
		
		expect(watcher)._update_test(good, test_result.success).once()
		watcher.beforeTest(good)
		watcher.addSuccess(good)

	def test_should_update_test_on_failure(self):
		watcher = self.watcher()

		bad = mock('bad').with_children(plugins=mock('bad plugins').with_methods(formatFailure=None))
		bad_err = mock('bad_err')

		expect(watcher)._update_test(bad, test_result.fail, bad_err).once()

		watcher.beforeTest(bad)
		watcher.handleFailure(bad, bad_err)

	def test_should_update_test_on_error(self):
		watcher = self.watcher()

		ugly = mock('ugly').with_children(plugins=mock('ugly plugins').with_methods(formatError=None))
		ugly_err = mock('ugly_err')
		expect(watcher)._update_test(ugly, test_result.error, ugly_err).once()

		watcher.beforeTest(ugly)
		watcher.handleError(ugly, ugly_err)

	def test_should_update_test_on_skip(self):
		watcher = self.watcher()

		skippy = mock('skippy')
		expect(watcher)._update_test(skippy, test_result.skip).once()
		watcher.beforeTest(skippy)
		watcher.afterTest(skippy)
	
	def test_should_not_run_tests_from_outside_current_root(self):
		path = mock('path')

		expect(file_util).relative(path).and_raise(file_util.FileOutsideCurrentRoot()).once()
		
		watcher = self.watcher()

		without_logging(lambda: self.assertEqual(watcher.wantFile(path), False), level=logging.ERROR)

	def test_should_save_state_on_finalize(self):
		watcher = self.watcher()

		expect(watcher)._send.once()
		watcher.finalize()




