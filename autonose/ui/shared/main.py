from data import Data, EOF
from page import Page

class Main(object):
	def __init__(self, delegate, input):
		self.delegate = delegate
		self.input = input
		self.work = []
		self.page = Page()

	def run(self):
		try:
			while not self.input.closed:
				line = self.input.readline()
				if line is None or line.strip() == EOF:
					break
				line = line.strip()
				if line:
					self.process_line(line)
		except KeyboardInterrupt:
			pass
		except StandardError:
			print "UI process input loop received exception:"
			import traceback
			traceback.print_exc()
		finally:
			self.delegate.exit()
	
	def process_line(self, line):
		node = Data.decode(line)
		self.page.process_node(node)
		self.delegate.update(self.page)
	
