import os
from multiprocessing import Process
import multiprocessing

from process import RunnerProcess
from main import Main

import logging
log = logging.getLogger(__name__)
info = log.info

class Launcher(object):
	"""
	On initialisation, forks a process which will run
	the passed-in callable (an App class, i.e gtk App or Cocoa App) with an
	event queue and and object representing the main (runner) process
	"""
	def __init__(self, result_queue, app_cls):
		self.ui_proc = self.fork(result_queue, app_cls)
	
	# run on child (ui) process
	@classmethod
	def child_init(cls, queue, app_cls, parent_pid):
		parent = RunnerProcess(pid=parent_pid, queue=queue)
		main = Main(runner_process=parent, app_cls=app_cls)
		main.run()

	def fork(self, queue, app_cls):
		self.queue = queue
		pid = os.getpid()
		proc = Process(name="autonose UI", target=self.child_init, args=(self.queue, app_cls, pid))
		proc.daemon = True
		proc.start()
		return proc

	def begin_new_run(self, current_time):
		pass
	
	def finalize(self):
		pass

	def is_running(self):
		return self.ui_proc in multiprocessing.active_children()

