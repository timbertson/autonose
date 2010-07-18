import os
import signal

class IPC(object):
	def __init__(self, pid, queue):
		self.queue = queue
		self.pid = pid
	
	def wait(self):
		pid, retcode = os.waitpid(self.pid, 0)
		return retcode
	
	def terminate(self):
		return os.kill(self.pid, signal.SIGINT)

