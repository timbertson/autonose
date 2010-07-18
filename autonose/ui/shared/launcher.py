import subprocess
import os
import sys
from multiprocessing import Process, Queue

from data import Data
from ipc import IPC

import logging
log = logging.getLogger(__name__)
info = log.info

# responsible for forking a process which will run
# the passed-in callable (an App class) with a queue
# and the pid of the main process
class Launcher(object):
	def __init__(self, nose_args, app):
		self.ui_proc = self.fork(app)
		self.setup_args(nose_args)
	
	# run on child (ui) process
	@classmethod
	def child_init(cls, queue, app, parent_pid):
		parent = IPC(pid=parent_pid, queue=queue)
		app(parent)

	def fork(self, app):
		self.queue = Queue()
		Data.queue = self.queue
		pid = os.getpid()
		proc = Process(name="autonose UI", target=self.child_init, args=(self.queue, app, pid))
		proc.daemon = True
		proc.start()
		return proc

	def setup_args(self, nose_args):
		nose_args.append('--xml')
		nose_args.append('--xml-formatter=%s' % (self._path_to_formatter(),))
	
	def _path_to_formatter(self):
		path = __name__.split('.')[:-1]
		path += ['data','Data']
		path = '.'.join(path)
		return path

	def begin_new_run(self, current_time):
		pass
	
	def finalize(self):
		pass

