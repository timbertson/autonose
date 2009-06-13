import subprocess
import os
import sys

from data import Data

import logging
log = logging.getLogger(__name__)
info = log.info

class Launcher(object):
	def __init__(self, nose_args = None, app_file = __file__):
		self.proc, self.output_stream = self.fork(app_file)
		Data.realStream = self.output_stream
		self.setup_args(nose_args)
	
	def fork(self, app_file):
		proc = subprocess.Popen(['python', app_file], stdin=subprocess.PIPE)
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

