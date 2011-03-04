import nose
import logging
import os
import time

from shared import file_util
from shared.file_util import FileOutsideCurrentRoot


# because the logcapture plugin
# sets logging to full throttle, we want to
# explicitly keep track of the log level
# requested by runner.py
actual_log_level = logging.INFO
def _log(lvl):
	log = logging.getLogger(__name__)
	def _(msg):
		if actual_log_level >= lvl:
			log.log(lvl, msg)
	return _

debug = _log(logging.DEBUG)
info = _log(logging.INFO)
warning = _log(logging.WARN)

from shared.test_result import TestResult, success, skip, error, fail, ResultEvent

class TestRun(ResultEvent):
	is_test=False
	def __init__(self, time):
		self.time = time
	
	def affect_state(self, state):
		pass

	def affect_page(self, page):
		page.start_new_run()

class Completion(ResultEvent):
	is_test=False

	def affect_page(self, page):
		page.finish()

def get_path(x): return x.path

class Watcher(nose.plugins.Plugin):
	name = 'autonose'
	score = 8000 # watcher is a mostly passive plugin so we shouldn't
	             # interfere with anyone else, however if others steal
	             # the handleError and handleFaure calls (as the
	             # xml plugin does), autonose fails to remember which
	             # tests failed - which is a Very Bad Thing (TM)
	enabled = True
	env_opt = 'AUTO_NOSE'
	
	def __init__(self, state_manager, *results_listeners):
		self.state_manager = state_manager
		self.results_listeners = results_listeners
		self._setup()
		super(self.__class__, self).__init__()
	
	def _send(self, *msg):
		[listener.send(*msg) for listener in self.results_listeners]
	
	def _setup(self):
		self.start_time = time.time()
		self.files_to_run = set(self.state_manager.affected).union(set(self.state_manager.bad))
		if len(self.state_manager.affected):
			warning("changed files: %s" % (self.state_manager.affected,))
		if len(self.state_manager.bad):
			info("bad files: %s" % (self.state_manager.bad,))
		if len(self.files_to_run):
			warning("files to run: %s" % (self.files_to_run,))
		self._send(TestRun(self.start_time))

	def options(self, parser, env=os.environ):
		pass

	def configure(self, options, conf=None):
		self.enabled = True

	def run_all(self):
		self.wantFile = lambda filename: None

	def wantFile(self, filename):
		try:
			rel_file = file_util.relative(filename)
		except FileOutsideCurrentRoot:
			warning("ignoring file outside current root: %s" % (filename,))
			return False
		
		debug("want file %s? %s" % (rel_file, "NO" if (rel_file not in self.files_to_run) else "if you like..."))
		debug("files to run are: %r" % (self.files_to_run,))
		if rel_file not in self.files_to_run:
			return False
		return None # do nose's default behaviour
	
	def beforeTest(self, test):
		self._current_test = test
	
	def _test_file(self, test):
		addr = test.address()
		err = RuntimeError("test.address does not contain a valid file: %s" % (addr,))
		if not addr: raise err

		file_path = addr[0]
		if not os.path.exists(file_path): raise err
		return file_util.relative(file_util.source(file_path))

	def _update_test(self, test, state, err=None):
		log_lvl = debug
		if state != 'success':
			log_lvl = info
		log_lvl("test finished: %s with state: %s" % (test, state))
		self._send(TestResult(
			state=state,
			id=test.id(),
			name=str(test),
			address=nose.util.test_address(test),
			err=err,
			run_start=self.start_time,
			path=self._test_file(test),
			outputs=self._capture_outputs(test)
		))
		self._current_test = None
		
	def addSuccess(self, test):
		self._update_test(test, success)
	
	def handleFailure(self, test, err):
		err = test.plugins.formatFailure(test, err) or err
		self._update_test(test, fail, err)
	
	def handleError(self, test, err):
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

	def _capture_outputs(self, test):
		outputs = []
		try:
			outputs.append(('stdout', test.capturedOutput))
		except AttributeError: pass

		try:
			outputs.append(('logging', test.capturedLogging))
		except AttributeError: pass
		return outputs
	
	def finalize(self, result=None):
		self._send(Completion())
	

