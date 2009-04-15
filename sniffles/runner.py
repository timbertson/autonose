#!/usr/bin/env python

import nose
import mandy
import os
import logging

# from watcher import Watcher

log = logging.getLogger(__name__)
debug = log.debug

class NullHandler(logging.Handler):
	def emit(self, record):
		pass

class Main(mandy.Command):
	def configure(self):
		self.opt('clear', bool, default=False, opposite=False, desc='reset all dependency information')
		self.opt('once', bool, default=False, opposite=False, desc='run all outdated tests and then exit')
		self.opt('debug', bool, default=False, opposite=False, desc='show debug output')
	
	def run(self, opts):
		self.opts = opts
		if opts.debug:
			logging.basicConfig(level=logging.DEBUG)
		else:
			logging.getLogger('sniffles').addHandler(NullHandler())
		import scanner
		state = scanner.filesystem_state()
		print '-'*80
		for key, items in state.items():
			print key
			print items
			print '='*20

if __name__ == '__main__':
	Main()
