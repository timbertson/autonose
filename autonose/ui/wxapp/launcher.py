import subprocess
import os
import sys

from data import Data

import logging
log = logging.getLogger(__name__)
info = log.info

class AppLauncher(object):
	def __init__(self, nose_args = None):
		self.proc, self.output_stream = self.fork()
		Data.realStream = self.output_stream
		self.setup_args(nose_args)
	
	def fork(self):
		proc = subprocess.Popen(['python', __file__], stdin=subprocess.PIPE)
		return proc, proc.stdin
	
	def setup_args(self, nose_args):
		path_to_formatter = __name__.split('.')[:-1]
		path_to_formatter += ['data','Data']
		path_to_formatter = '.'.join(path_to_formatter)
		nose_args.append('--xml')
		nose_args.append('--xml-formatter=%s' % (path_to_formatter,))
		try:
			del os.environ['NOSE_REDNOSE']
		except KeyError: pass

	def finalize(self):
		info("closing ui STDIN...")
		self.output_stream.close()
		info("waiting for UI to finish")
		retcode = self.proc.wait()
		info("UI finished with return code %s" % (retcode,))
		#TODO: do we care?
		# if retcode != 0:
		# 	raise RuntimeError("return code (%s) from UI is nonzero..." % (retcode,))

	def begin_new_run(self, current_time):
		Data.writeNodeNamed('new_run')

if __name__ == '__main__':
	import app
	app.App()

