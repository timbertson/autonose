#!/usr/bin/env python

import nose
import mandy
import os
import sys
import time
import logging
import traceback

import scanner
import watcher

log = logging.getLogger(__name__)
debug = log.debug
info = log.info

class NullHandler(logging.Handler):
	def emit(self, record):
		pass

class Main(mandy.Command):
	def configure(self):
		self._extra_nose_args = []
		# run control
		self.opt('clear', bool, default=False, opposite=False, desc='reset all dependency information')
		self.opt('once', bool, default=False, opposite=False, desc='run all outdated tests and then exit (uses --console)')
		self.opt('wait', int, default=2, desc='sleep time (between filesystem scans)')
		
		# logging
		self.opt('debug', bool, default=False, opposite=False, desc='show debug output')
		self.opt('info', bool, default=False, opposite=False, desc='show more info about what files have changed')
		
		# UI
		self.opt('console', bool, default=False, desc='use the console interface (no GUI)')

		# nose options
		self.opt('config', str, default=None, desc='nosetests config file')
		self.opt('nose-arg', short='x', default='', desc='additional nose arg (use multiple times to add many arguments)', action=self._append_nose_arg)
		#TODO: --direct -> run only files that have changed, and their direct imports
	
	def _append_nose_arg(self, val):
		self._extra_nose_args.append(val)
		
	def run(self, opts):
		self.opts = opts
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
			log.error(e.message)
			log.error(traceback.format_exc())
			raise
		finally:
			if self.ui is not None:
				info("finalizing UI")
				self.ui.finalize()
	
	def init_logging(self):
		format = '[%(levelname)s] %(name)s: %(message)s'
		lvl = logging.ERROR
		if self.opts.debug:
			lvl = logging.DEBUG
		elif self.opts.info:
			lvl = logging.INFO
		logging.basicConfig(level=lvl, format=format)

	def init_nose_args(self):
		self.nose_args = ['nosetests','--nologcapture', '--exe']
		if self.opts.config is not None:
			self.nose_args.append('--config=%s' % (self.opts.config))

	def save_init_modules(self):
		self._sys_modules = set(sys.modules.keys())

	def restore_init_modules(self):
		for modname in set(sys.modules.keys()).difference(self._sys_modules):
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
			self.ui = Launcher(self.nose_args, App.script)
		except StandardError:
			import traceback
			traceback.print_exc()
			print "UI load failed - falling back to basic console"
			print '-'*40
			time.sleep(3)
			return basic()
		
	def run_with_state(self, state):
		info("running with %s affected and %s bad files..." % (len(state.affected), len(state.bad)))
		self.restore_init_modules()
		self.ui.begin_new_run(time.localtime())
		watcher_plugin = watcher.Watcher(state)
		watcher_plugin.enable()
		nose_args = self.nose_args + self._extra_nose_args
		
		plugins = getattr(self.ui, 'addplugins', []) #FIXME: remove once nosexml is packaged externally

		nose.run(argv=nose_args, addplugins = plugins + [watcher_plugin])

def main(argv=None):
	try:
		Main()
		sys.exit(0)
	except KeyboardInterrupt:
		sys.exit(1)

if __name__ == '__main__':
	main()

