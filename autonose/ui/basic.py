import time
import subprocess
import sys
import termstyle
from autonose.watcher import TestRun
from autonose.shared.test_result import ResultEvent

class Basic(object):
	"""
	The main event handler for the basic (console) runner.
	"""
	def __init__(self, proc):
		proc.receive[ResultEvent] = self.process

	def process(self, event):
		if isinstance(event, TestRun):
			print "\n" * 10
			subprocess.call('clear')
			msg = "# Running tests at %s  " % (time.strftime("%H:%M:%S"),)
	
			print >> sys.stderr, termstyle.inverted(termstyle.bold(msg))
			print >> sys.stderr, ""

