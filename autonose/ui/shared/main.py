from data import Data
from page import Page

class Main(object):
	def __init__(self, delegate, queue):
		self.delegate = delegate
		self.queue = queue
		self.work = []
		self.page = Page()

	def run(self):
		try:
			while True:
				node = self.queue.get()
				self.page.process_node(node)
				self.delegate.update(self.page)
		except KeyboardInterrupt:
			pass
		except StandardError:
			print "UI process input loop received exception:"
			import traceback
			traceback.print_exc()
		finally:
			self.delegate.exit()
	
