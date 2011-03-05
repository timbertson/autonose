#!/usr/bin/env python

import nose
import sys
import time
import logging
import logging.config
import traceback
from optparse import OptionParser
import paragram as pg

import scanner
import watcher
from shared.test_result import ResultEvent

log = logging.getLogger('runner')
debug = log.debug
info = log.info
logging.getLogger('paragram').setLevel(logging.WARN)

class NullHandler(logging.Handler):
	def emit(self, record):
		pass

class MultiOutputQueue(object):
	def __init__(self, *output_queues):
		self.output_queues = output_queues
	
	def put(self, o):
		[queue.put(o) for queue in self.output_queues]

class Main(object):
	def __init__(self):
		parser = OptionParser()
		# run control
		parser.add_option('--clear', action='store_true', default=False, help='reset all dependency information')
		parser.add_option('--once', action='store_true', default=False, help='run all outdated tests and then exit (uses --console)')
		parser.add_option('--all', action='store_true', default=False, help='always run all tests - no filtering')
		parser.add_option('--dump-state', action='store_true', default=False, help='just dump the saved dependency state')
		
		# logging
		parser.add_option('--debug', action="store_true", default=False, help='show debug output')
		parser.add_option('--info', action="store_true", default=False, help='show more info about what files have changed')
		parser.add_option('--log-only', action="store", default=None, help='restrict logging to the given module(s)')
		
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
		if self.opts.clear:
			scanner.reset()
		state_manager = scanner.load()
		if self.opts.dump_state:
			print repr(state_manager.state)
			return
		self.init_ui()
		try:
			self.run_forever(state_manager)
		except Exception, e:
			pg.main.terminate(e)
			raise
	
	def monitor_state_changes(self, proc, state_manager):
		iterator = state_manager.state_changes()

		@proc.receive('next', pg.Process)
		def next(msg, caller):
			iterator.next()
			caller.send('state_changed')

	def run_when_state_changes(self, proc, state_manager, state_monitor_proc):
		@proc.receive('state_changed')
		def state_changed(msg):
			self.run_with_state(state_manager, proc)
			state_monitor_proc.send('next', proc)

		@proc.receive('focus_on', str)
		def focus_on(msg, test_id):
			self.test_id = test_id or None
			self.run_with_state(state_manager, proc)

		@proc.receive('start')
		def start(msg):
			state_monitor_proc.send('next', proc)

	def run_forever(self, state_manager):
		self.state_listener = pg.main.spawn_link(
			target=self.state_saver,
			name='state-saver',
			args=(state_manager.state,),
			kind=pg.ThreadProcess)

		self.run_with_state(state_manager, pg.main)
		if self.opts.once:
			pg.main.terminate()
			return

		# now set up processes to run forever
		monitor_state_changes = pg.main.spawn_link(
			target=self.monitor_state_changes,
			name='monitor-state-changes',
			args=(state_manager,),
			kind=pg.ThreadProcess)

		run_triggerer = pg.main.spawn_link(
			target=self.run_when_state_changes,
			name='run-on-state-change',
			args=(state_manager, monitor_state_changes),
			kind=pg.ThreadProcess)

		self.ui.send('use_runner', run_triggerer)
		run_triggerer.send('start')

	def init_logging(self):
		format = '[%(levelname)s] %(name)s: %(message)s'
		lvl = logging.WARNING
		if self.opts.debug:
			lvl = logging.DEBUG
		elif self.opts.info:
			lvl = logging.INFO
		logging.basicConfig(level=lvl, format=format)

		if self.opts.log_only:
			for name in self.opts.log_only.split(","):
				level = logging.DEBUG
				if ":" in name:
					name, level = name.split(":")
					level = getattr(logging, level)
				logging.getLogger(name).setLevel(level)
				logging.info("set extended logging on logger %s" % (name,))
		# since watcher runs in the nose process, it needs to be careful when logging...
		watcher.actual_log_level = logging.getLogger('watcher').level

	def init_nose_args(self):
		self.nose_args = ['nosetests','--exe']
		if self.opts.config is not None:
			self.nose_args.append('--config=%s' % (self.opts.config))
		self.nose_args.extend(self.opts.nose_args)
		self.test_id = None

	def init_ui(self):
		self.ui = None
		def basic():
			from ui.basic import Basic
			self.ui = pg.main.spawn_link(target=Basic, kind=pg.ThreadProcess, name="basic UI")

		if self.opts.console or self.opts.once:
			return basic()

		from ui.platform import default_app
		try:
			App = default_app()
			from ui.shared import Main as UIMain
			self.ui = pg.main.spawn_link(target=UIMain, args=(App,), name="UI", kind=pg.OSProcess)
		except StandardError:
			traceback.print_exc()
			print "UI load failed - falling back to basic console"
			print '-'*40
			time.sleep(3)
			return basic()
	
	def state_saver(self, proc, state):
		proc.receive[watcher.Completion] = lambda completion: scanner.save(state)
		proc.receive[ResultEvent] = lambda event: event.affect_state(state)

	def run_with_state(self, state_manager, proc):
		info("running with %s affected and %s bad files... (%s files total)" % (len(state_manager.affected), len(state_manager.bad), len(state_manager.state)))
		debug("state is: %r" % (state_manager.state,))
		args = self.nose_args[:]
		if self.test_id:
			args.append(self.test_id)
			# when only running a single test, we can't reliably update the state records
			listeners = [self.ui]
		else:
			listeners = [self.ui, self.state_listener]

		debug("args are: %r" % (args,))
		watcher_plugin = watcher.Watcher(state_manager, *listeners)
		if self.opts.all:
			watcher_plugin.run_all()

		def run_tests(proc):
			nose.run(argv=args, addplugins=[watcher_plugin])
			proc.terminate()

		runner = proc.spawn(target=run_tests, name="nose test runner", kind=pg.OSProcess)
		runner.wait()
		if runner.error:
			proc.terminate(runner.error)
		#pg.graph()

def main():
	#pg.enable_graphs()
	try:
		Main().run()
		sys.exit(0)
	except KeyboardInterrupt:
		sys.exit(1)

if __name__ == '__main__':
	main()

