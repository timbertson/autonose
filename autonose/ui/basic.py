import time
import subprocess
import sys
import termstyle

from base import BaseUI

class Basic(BaseUI):
	def begin_new_run(self, current_time):
		print "\n" * 10
		subprocess.call('clear')

		print >> sys.stderr, termstyle.inverted(termstyle.bold("# Running tests at %s  " % (time.strftime("%H:%m:%S", current_time))))
		print >> sys.stderr, ""

