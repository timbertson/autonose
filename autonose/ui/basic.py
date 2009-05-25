import time
import subprocess
import sys
import termstyle

def has_rednose():
	try:
		__import__('rednose')
		return True
	except ImportError:
		return False

class Basic(object):
	def __init__(self, nose_args):
		if has_rednose():
			nose_args.append('--rednose')

	def finalize(self):
		pass
	
	def begin_new_run(self, current_time):
		print "\n" * 10
		# subprocess.call('clear')

		print >> sys.stderr, termstyle.inverted(termstyle.bold("# Running tests at %s  " % (time.strftime("%H:%m:%S", current_time))))
		print >> sys.stderr, ""

