import sys
import logging
from shared.test_result import ResultEvent

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
		proc.receive[ResultEvent] = self.process
		import watcher
		proc.receive[watcher.TestRun] = self.process
		import paragram as pg
		@proc.receiver(pg.Any)
		def handle(thing):
			logging.error(type(thing))
			logging.error(ResultEvent)
			logging.error(isinstance(thing, ResultEvent))
			logging.error(thing)
			raise RuntimeError(type(thing))

	def process(self, event):
		log.debug("processing event: %r" % (event,))
		event.affect_page(self.page)
		self.delegate.update(self.page)
	
	def terminate(self):
		self.proc.terminate()
	
