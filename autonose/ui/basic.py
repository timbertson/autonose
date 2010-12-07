import time
import subprocess
import sys
import termstyle

class Basic(object):
	"""
	The main loop for the basic (console) runner.
	Spawns its own thread.
	"""
	def __init__(self, event_queue):
		self.event_queue = event_queue
		import threading
		self.thread = threading.Thread(target=self.run)
		self.thread.daemon = True
		self.thread.start()
	
	def run(self):
		while True:
			self.event_queue.get().affect_page(self)
	
	def finalize(self): pass
	def finish(self): pass
	def test_complete(self, *args, **kwargs): pass
	def is_running(self): return self.thread.is_alive()

	def start_new_run(self):
		print "\n" * 10
		subprocess.call('clear')
		msg = "# Running tests at %s  " % (time.strftime("%H:%M:%S"),)
 
		print >> sys.stderr, termstyle.inverted(termstyle.bold(msg))
		print >> sys.stderr, ""

