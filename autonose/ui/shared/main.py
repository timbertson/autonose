import sys

from data import Data
from page import Page

class Main(object):
	def __init__(self, delegate):
		self.delegate = delegate
		self.work = []
		self.page = Page()

	def run(self):
		print "RUNNING"
		try:
			
			while not sys.stdin.closed:
				line = sys.stdin.readline()
				self.process_line(line)
				if not line:
					print "UI received EOF"
					break
		except KeyboardInterrupt:
			pass
		except StandardError:
			import traceback
			traceback.print_exc()
		finally:
			self.delegate.exit()
	
	def process_line(self, line):
		node = Data.decode(line)
		self.page.process_node(node)
		self.delegate.update(self.page)

