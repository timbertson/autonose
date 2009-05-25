#!/usr/bin/env python

import nose
import mandy
import os
import sys
import time
import logging

import scanner
import watcher

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
		self.opt('info', bool, default=False, opposite=False, desc='show more info about what files have changed')
		self.opt('wait', int, default=5, desc='sleep time (between filesystem scans)')
		self.opt('config', str, default=None, desc='nosetests config file')
		self.opt('curses', bool, default=False, desc='use the curses interface')
		self.opt('osx', bool, default=False, desc='use the cocoa interface')
		self.opt('wx', bool, default=False, desc='use the wxpython interface')
	
	def run(self, opts):
		self.opts = opts
		self.init_logging()
		self.init_nose_args()
		self.init_ui()
		self.save_init_modules()
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
				if self.opts.once:
					break
				debug("sleeping (%s)..." % (self.opts.wait,))
				time.sleep(self.opts.wait)
		finally:
			if self.ui is not None:
				self.ui.finalize()
	
	def init_logging(self):
		if self.opts.debug:
			logging.basicConfig(level=logging.DEBUG)
			self.info()
		elif self.opts.info:
			logging.basicConfig(level=logging.INFO)
		else:
			logging.getLogger().addHandler(NullHandler())

	def init_nose_args(self):
		self.nose_args = ['nosetests','--autorun']
		if self.opts.config is not None:
			self.nose_args.append('--config=%s' % (self.opts.config))

	def save_init_modules(self):
		self._sys_modules = set(sys.modules.keys())

	def restore_init_modules(self):
		for modname in set(sys.modules.keys()).difference(self._sys_modules):
			del(sys.modules[modname])
	
	def init_ui(self):
		self.ui = None
		if self.opts.curses:
			from ui.terminal import Terminal
			self.ui = Terminal(self.nose_args)
		elif self.opts.osx:
			from ui.cocoa import Cocoa
			self.ui = Cocoa(self.nose_args)
		elif self.opts.wx:
			from ui.wxapp import WxApp
			self.ui = WxApp(self.nose_args)
		else:
			from ui.basic import Basic
			self.ui = Basic(self.nose_args)
	
	def run_with_state(self, state):
		debug("running with %s affected files..." % (len(state.affected)))
		self.restore_init_modules()
		self.ui.begin_new_run(time.localtime())
		nose.run(argv=self.nose_args)

	def info(self):
		state = scanner.scan()
		print '-'*80
		attrs = ['changed','added','removed','affected']
		for key in attrs:
			print key
			items = getattr(state, key)
			for item in items:
				print repr(item)
			print '='*20


def main(argv=None):
	try:
		Main()
		sys.exit(0)
	except KeyboardInterrupt:
		sys.exit(1)

if __name__ == '__main__':
	main()

