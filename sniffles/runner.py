#!/usr/bin/env python

import nose
import mandy
import os
import logging

from watcher import Watcher

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
		import watcher
		deps = watcher.load_dependencies()
		all_stamps = []
		print(deps)
		for stamp_set in deps.values():
			for stamp in stamp_set:
				if stamp.path not in all_stamps:
					all_stamps.append(stamp)
					
		scanner.FSChanges(os.getcwd(), all_stamps).scan()
		nose.run(plugins=[Watcher()], argv=['--with-sniffles','--debug=sniffles'])


if __name__ == '__main__':
	Main()
