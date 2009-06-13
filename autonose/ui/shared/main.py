import sys
import threading

from data import Data
from page import Page

class Main(object):
	def __init__(self, delegate):
		self.delegate = delegate
		self.work = []
		self.page = Page()
		self.lock = threading.Lock()

	def run(self):
		import os
		try:
			while not sys.stdin.closed:
				line = sys.stdin.readline()
				self.process_line(line)
				if not line:
					print "UI received EOF"
					break
		except KeyboardInterrupt:
			pass
		finally:
			self.do(self.delegate.exit)
	
	def process_line(self, line):
		node = Data.decode(line)
		self.page.process_node(node)
		self.do(lambda: self.delegate.update(self.page))
	
	def do(self, func):
		self.lock.acquire()
		self.work.append(func)
		self.lock.release()
	
	def on_idle(self, *args):
		self.lock.acquire()
		if self.work:
			for work_item in self.work:
				work_item()
			self.work = []
		self.lock.release()
