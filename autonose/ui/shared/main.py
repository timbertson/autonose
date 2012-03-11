import logging
from autonose.shared.test_result import ResultEvent
from autonose.watcher import TestRun
import paragram as pg

from page import Page

log = logging.getLogger(__name__)

class Main(object):
	"""
	The main-loop of all graphical App classes
	(currently, gtkapp and cocoa-app)
	"""
	def __init__(self, proc, app_cls):
		self.delegate = app_cls(self)
		self.proc = proc
		self.page = Page()
		self.run_trigger = None

		@proc.receive('use_runner', pg.Process)
		def use_runner(msg, runner):
			self.runner = runner

		proc.receive[ResultEvent] = self.process
		proc.receive[TestRun] = self.process

	def run_just(self, test_id):
		self.runner.send('focus_on', test_id)

	def run_normally(self):
		self.runner.send('focus_on', None)

	def process(self, event):
		log.debug("processing event: %r" % (event,))
		event.affect_page(self.page)
		self.delegate.update(self.page)
	
	def terminate(self):
		self.proc.terminate()
	
