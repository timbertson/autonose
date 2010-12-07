from page import Page
import logging
log = logging.getLogger(__name__)

class Main(object):
	def __init__(self, delegate, queue):
		self.delegate = delegate
		self.queue = queue
		self.work = []
		self.page = Page()

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
	
	def process(self, event):
		log.debug("processing event: %r" % (event,))
		event.affect_page(self.page)
	
