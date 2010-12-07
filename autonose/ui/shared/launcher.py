import subprocess
import os
import sys
from multiprocessing import Process, Queue

from ipc import IPC

import logging
log = logging.getLogger(__name__)
info = log.info

# responsible for forking a process which will run
# the passed-in callable (an App class) with a queue
# and the pid of the main process
class Launcher(object):
	def __init__(self, result_queue, app):
		self.ui_proc = self.fork(result_queue, app)
	
	# run on child (ui) process
	@classmethod
	def child_init(cls, queue, app, parent_pid):
		parent = IPC(pid=parent_pid, queue=queue)
		app(parent)

	def fork(self, queue, app):
		self.queue = queue
		pid = os.getpid()
		proc = Process(name="autonose UI", target=self.child_init, args=(self.queue, app, pid))
		proc.daemon = True
		proc.start()
		return proc

	def begin_new_run(self, current_time):
		pass
	
	def finalize(self):
		pass

