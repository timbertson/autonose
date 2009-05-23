#!/usr/bin/env python

import nose
import mandy
import os
import sys
import time
import logging
import subprocess

import scanner
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
		self.opt('changelog', bool, default=False, opposite=False, desc='show more info about what files have changed')
		self.opt('wait', int, default=5, desc='sleep time (between filesystem scans)')
		self.opt('config', str, default=None, desc='nosetests config file')
		self.opt('curses', bool, default=False, desc='use the curses interface')
	
	def run(self, opts):
		self.opts = opts
		if opts.debug:
			logging.basicConfig(level=logging.DEBUG)
		else:
			logging.getLogger('autonose').addHandler(NullHandler())

		if opts.debug:
			self.info()
		sleep_time = opts.wait
		first_run = True
		config_file = opts.config
		self.ui = None
		if opts.curses:
			from ui.terminal import Terminal
			self.ui = Terminal()
		self.nose_args = ['--autorun']
		if config_file is not None:
			self.nose_args.append('--config=%s' % (config_file))
		if opts.debug:
			self.nose_args.append('--debug=autonose')
		elif opts.changelog:
			self.nose_args.append('--debug=autonose.shared.state.summary')
		try:
			while True:
				state = scanner.scan()
				if state.anything_changed() or first_run:
					first_run = False
					self.run_with_state(state)
				if opts.once:
					break
				debug("sleeping (%s)..." % (sleep_time,))
				time.sleep(sleep_time)
		finally:
			if self.ui is not None:
				self.ui.finalize()
	
	def run_with_state(self, state):
		debug("running with %s affected files..." % (len(state.affected)))
		self.clear()
		self.timestamp()
		#todo: run this in-process (currently it doesn't seem to reload tested modules properly...)
		subprocess.call(['nosetests'] + self.nose_args)

	def timestamp(self):
		print >> sys.stderr, "# Running tests at %s  " % (time.strftime("%H:%m:%S"))
		print >> sys.stderr, ""
	
	def clear(self):
		print "\n" * 80
		subprocess.call('clear')
	
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

