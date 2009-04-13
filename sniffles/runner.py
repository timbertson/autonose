#!/usr/bin/env python

import nose
import mandy

from watcher import Watcher

class Main(mandy.Command):
	def configure(self):
		self.opt('clear', bool, default=False, opposite=False, desc='reset all dependency information')
		self.opt('once', bool, default=False, opposite=False, desc='run all outdated tests and then exit')
	
	def run(self, opts):
		self.opts = opts
		nose.run(plugins=[Watcher()], argv=['--with-sniffles','--debug=sniffles'])


if __name__ == '__main__':
	Main()
