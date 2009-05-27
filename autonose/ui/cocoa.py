import os
import threading
from Cocoa import *

from base import BaseUI

class Cocoa(BaseUI):
	def __init__(self, nose_args):
		self.setup_args(nose_args)
		print dir(Cocoa)
		self.app = NSApplication.sharedApplication()
		threading.Thread(target=self._main).start()
	
	def _main(self):
		# NSBundle.loadNibNamed_owner_("main", NSApp)
		self.app.run()
	
	def setup_args(self, nose_args):
		nose_args += ['--xml', '--xml-formatter=nosexml.PrettyPrintFormatter']
		try:
			del os.environ['NOSE_REDNOSE']
		except KeyError: pass

	def finalize(self):
		pass

	def begin_new_run(self, current_time):
		pass


