#!/usr/bin/env python

import nose
import os
import sys
import time
import logging
import traceback
from optparse import OptionParser

import scanner
import watcher

log = logging.getLogger(__name__)
debug = log.debug
info = log.info

class NullHandler(logging.Handler):
	def emit(self, record):
		pass

class Main(object):
	def __init__(self):
		self.configure()

	def configure(self):
		parser = OptionParser()
		# run control
		parser.add_option('--clear', action='store_true', default=False, help='reset all dependency information')
		parser.add_option('--once', action='store_true', default=False, help='run all outdated tests and then exit (uses --console)')
		parser.add_option('--wait', type="int", default=2, help='sleep time (between filesystem scans)')
		parser.add_option('--all', action='store_true', default=False, help='always run all tests - no filtering')
		
		# logging
		parser.add_option('--debug', action="store_true", default=False, help='show debug output')
		parser.add_option('--info', action="store_true", default=False, help='show more info about what files have changed')
		
		# UI
		parser.add_option('--console', action="store_true", default=False, help='use the console interface (no GUI)')

		# nose options
		parser.add_option('--config', default=None, help='nosetests config file')
		parser.add_option('-x', '--nose-arg', default=[], dest='nose_args', action="append", help='additional nose arg (use multiple times to add many arguments)') #TODO: --direct -> run only files that have changed, and their direct imports
		opts, args = parser.parse_args()
		if args:
			parser.print_help()
			sys.exit(2)
		self.opts = opts
	
	def run(self):
		self.init_logging()
		self.init_nose_args()
		self.init_ui()
		self.save_init_modules()
		if self.opts.clear:
			scanner.reset()
		self.run_loop()
	
	def run_loop(self):
		first_run = True
		try:
			while True:
				state = scanner.scan()
				if state.anything_changed() or first_run:
					first_run = False
					watcher.global_state = state
					self.run_with_state(state)
				scanner.save(state)
				if self.opts.once:
					break
				debug("sleeping (%s)..." % (self.opts.wait,))
				time.sleep(self.opts.wait)
		except Exception, e:
			log.error(e)
			log.error(traceback.format_exc())
			raise
		finally:
			if self.ui is not None:
				info("finalizing UI")
				self.ui.finalize()
	
	def init_logging(self):
		format = '[%(levelname)s] %(name)s: %(message)s'
		lvl = logging.WARNING
		if self.opts.debug:
			lvl = logging.DEBUG
		elif self.opts.info:
			lvl = logging.INFO
		logging.basicConfig(level=lvl, format=format)

	def init_nose_args(self):
		self.nose_args = ['nosetests','--nologcapture', '--nocapture', '--exe', '--with-doctest']
		if self.opts.config is not None:
			self.nose_args.append('--config=%s' % (self.opts.config))
		self.nose_args.extend(self.opts.nose_args)

	def save_init_modules(self):
		import StringIO
		self._sys_modules = set(sys.modules.keys())
		[logging.debug("saving sys.modules[%s]" % (modname, )) for modname in self._sys_modules]

	def restore_init_modules(self):
		for modname in set(sys.modules.keys()).difference(self._sys_modules):
			if modname.split(".")[0] == 'autonose':
				logging.debug("ignoring sys.modules[%s]" % (modname,))
				continue
			logging.debug("removing sys.modules[%s]" % (modname,))
			del(sys.modules[modname])
	
	def init_ui(self):
		self.ui = None
		def basic():
			from ui.basic import Basic
			self.ui = Basic(self.nose_args)

		if self.opts.console or self.opts.once:
			return basic()

		from ui.platform import default_app
		try:
			App = default_app()
			from ui.shared import Launcher
			self.ui = Launcher(self.nose_args, App)
		except StandardError:
			import traceback
			traceback.print_exc()
			print "UI load failed - falling back to basic console"
			print '-'*40
			time.sleep(3)
			return basic()
		
	def run_with_state(self, state):
		info("running with %s affected and %s bad files..." % (len(state.affected), len(state.bad)))
		debug("args are: %r" % (self.nose_args,))
		self.restore_init_modules()
		self.ui.begin_new_run(time.localtime())
		watcher_plugin = watcher.Watcher(state)
		plugins = getattr(self.ui, 'plugins', [])
		if not self.opts.all:
			watcher_plugin.enable()
		nose.run(argv=self.nose_args, addplugins = plugins + [watcher_plugin])

def main():
	try:
		Main().run()
		sys.exit(0)
	except KeyboardInterrupt:
		sys.exit(1)

if __name__ == '__main__':
	main()

