import sys
import logging

from page import Page

log = logging.getLogger(__name__)

class Main(object):
	"""
	The main-loop of all graphical App classes
	(currently, gtkapp and cocoa-app)
	"""
	def __init__(self, runner_process, app_cls):
		self.delegate = app_cls(self)
		self.runner = runner_process
		self.queue = runner_process.queue
		self.page = Page()
	
	def terminate(self):
		self.runner_process.terminate()

	def run(self):
		try:
			while True:
				self.process(self.queue.get())
				self.delegate.update(self.page)
		except KeyboardInterrupt:
			pass
		except StandardError:
			print "UI process input loop received exception:"
			import traceback
			traceback.print_exc()
		finally:
			self.delegate.exit()
			sys.exit(1)
	
	def process(self, event):
		log.debug("processing event: %r" % (event,))
		event.affect_page(self.page)
	
