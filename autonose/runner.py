#!/usr/bin/env python

import nose
import sys
import time
import logging
import traceback
import multiprocessing
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
		parser.add_option('--all', action='store_true', default=False, help='always run all tests - no filtering')
		parser.add_option('--dump-state', action='store_true', default=False, help='just dump the saved dependency state')
		
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
		if self.opts.clear:
			scanner.reset()
		self.run_forever()
	
	def run_forever(self):
		try:
			state_manager = scanner.load()
			if self.opts.dump_state:
				for item in state_manager.state.values():
					print repr(item)
				return
			self.run_with_state(state_manager)
			if self.opts.once:
				return
			for point_in_time in state_manager.state_changes():
				# this is a generator, it will yield forever
				self.run_with_state(state_manager)
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
		
	def run_with_state(self, state_manager):
		info("running with %s affected and %s bad files... (%s files total)" % (len(state_manager.affected), len(state_manager.bad), len(state_manager.state)))
		debug("state is: %r" % (state_manager.state,))
		debug("args are: %r" % (self.nose_args,))
		self.ui.begin_new_run(time.localtime())
		watcher_plugin = watcher.Watcher(state_manager)
		plugins = getattr(self.ui, 'plugins', [])
		if not self.opts.all:
			watcher_plugin.enable()

		runner = multiprocessing.Process(
			name="nosetests",
			target=nose.run,
			kwargs=dict(argv=self.nose_args, addplugins = plugins + [watcher_plugin])
		)
		runner.daemon = True
		runner.start()
		runner.join()
		scanner.save(state_manager.state)

def main():
	try:
		Main().run()
		sys.exit(0)
	except KeyboardInterrupt:
		sys.exit(1)

if __name__ == '__main__':
	main()

