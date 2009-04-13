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
		dependencies = watcher.load_dependencies()
		all_stamps = self._flatten_filestamps(dependencies)
		scanner.FSChanges(os.getcwd(), all_stamps).scan()
		debug('-'*80)
		watcher = Watcher()
		watcher.enabled = True

		testprog = nose.core.TestProgram(exit=False, plugins=[watcher], argv=['--debug=sniffles', '--verbose', '--with-sniffles'])
		print repr(testprog.showPlugins())
		# nose.run(plugins=[watcher], argv=['--debug=sniffles', '--verbose'])
	
	def _flatten_filestamps(self, dependencies):
		all_stamps = []
		print(dependencies)
		for stamp_set in dependencies.values():
			for stamp in stamp_set:
				if stamp.path not in all_stamps:
					all_stamps.append(stamp)
		return all_stamps


if __name__ == '__main__':
	Main()
