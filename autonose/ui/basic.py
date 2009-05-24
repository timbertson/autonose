import time
import subprocess
import sys
import termstyle

class Basic(object):
	def finalize(self):
		pass
	
	def begin_new_run(self, current_time):
		print "\n" * 10
		# subprocess.call('clear')

		print >> sys.stderr, termstyle.inverted(termstyle.bold("# Running tests at %s  " % (time.strftime("%H:%m:%S", current_time))))
		print >> sys.stderr, ""

