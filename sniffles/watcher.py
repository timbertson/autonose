import nose
import sys
import logging
import os
import time

from shared import file_util
import scanner

log = logging.getLogger(__name__)
debug = log.debug

from shared.test_result import TestResult, TestResultSet, success, skip, error, fail

class Watcher(nose.plugins.Plugin):
	name = 'sniffles'
	score = 800
	enabled = False
	env_opt = 'NOSE_SNIFFLES'
	
	def __init__(self, state=None):
		self.state = state
		super(self.__class__, self).__init__()
	
	def _setup(self):
		if self.state is None:
			self.state = scanner.scan()
		self.start_time = time.time()
		get_path = lambda x: x.path
		self.files_to_run = set(self.state.affected).union(set(self.state.bad))
		debug("changed files: %s" % (map(get_path, self.state.affected),))
		debug("bad files: %s" % (map(get_path, self.state.bad),))

	def options(self, parser, env=os.environ):
		parser.add_option(
			"--sniffles", action="store_true",
			default=env.get(self.env_opt), dest="sniffles",
			help="enable sniffles plugin")

	def configure(self, options, conf):
		if options.sniffles:
			self.enabled = True
			self._setup()

	def wantFile(self, filename):
		debug("want file %s? %s" % (filename, "NO" if (file_util.relative(filename) not in self.files_to_run) else "if you like..."))
		if file_util.relative(filename) not in self.files_to_run:
			return False
	
	def beforeTest(self, test):
		self._current_test = test
	
	def _test_file(self, test):
		file_path = test.address()[0]
		if not os.path.exists(file_path):
			raise RuntimeError("test.address does not contain a valid file: %s" % (test.address(),))
		return file_util.relative(file_util.source(file_path))

	def _update_test(self, test, state, err=None):
		debug("test finished: %s with state: %s" % (test, state))
		result = TestResult(state, test, err, self.start_time)
		
		filestamp = self.state[self._test_file(test)]
		filestamp.info.add(result)
		self._current_test = None
		debug(result)
		
	def addSuccess(self, test):
		self._update_test(test, success)
	
	def addFailure(self, test, err):
		err = test.plugins.formatFailure(test, err) or err
		self._update_test(test, fail, err)
	
	def addError(self, test, err):
		err = test.plugins.formatError(test, err) or err
		self._update_test(test, error, err)
	
	def _addSkip(self, test):
		self._update_test(test, skip)
	
	def afterTest(self, test):
		if self._current_test is not None:
			if self._current_test is not test:
				raise RuntimeError(
					"result for %s was never recorded, but this test is %s" %
					(self._current_test, test))
			self._addSkip(self._current_test)
		debug('-'*80)

	def finalize(self, result):
		debug(self.state)
		scanner.save()

