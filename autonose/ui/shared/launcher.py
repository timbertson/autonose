import subprocess
import os
import sys

from data import Data, EOF
from ipc import IPC

import logging
log = logging.getLogger(__name__)
info = log.info

class Launcher(object):
	def __init__(self, nose_args, script_file):
		self.ui_proc = self.fork(script_file)
		Data.realStream = self.ui_proc.stream
		self.setup_args(nose_args)
	
	def fork(self, script_file):
		readable, writable = os.pipe()
		readable, writable = os.fdopen(readable), os.fdopen(writable, 'w')
		
		main_pid = os.getpid()
		ui_pid = os.fork()
		
		if ui_pid == 0: # child code
			writable.close() # unneeded in child
			os.execlp('python', 'python', script_file, str(main_pid), str(readable.fileno()))
			raise SystemExit(1) # execlp never returns
		readable.close() # unneeded in parent
		return IPC(pid=ui_pid, stream=writable)
	
	def setup_args(self, nose_args):
		nose_args.append('--xml')
		nose_args.append('--xml-formatter=%s' % (self._path_to_formatter(),))
	
	def _path_to_formatter(self):
		path = __name__.split('.')[:-1]
		path += ['data','Data']
		path = '.'.join(path)
		return path

	def finalize(self):
		info("closing ui stream...")
		try:
			self.ui_proc.stream.write(EOF + '\n')
			self.ui_proc.stream.flush()
			self.ui_proc.stream.close()
			info("waiting for UI to finish")
			retcode = self.ui_proc.wait()
			info("UI finished with return code %s" % (retcode,))
			#TODO: do we care?
			# if retcode != 0:
			# 	raise RuntimeError("return code (%s) from UI is nonzero..." % (retcode,))
		except KeyboardInterrupt:
			info("UI signalled us back - ignoring")

	def begin_new_run(self, current_time):
		pass

	@staticmethod
	def run_ui(func):
		pid, fd = map(int, sys.argv[1:])
		ipc = IPC(pid, os.fdopen(fd, 'r'))
		return func(ipc)
	

	#FIXME: remove once nosexml is packaged externally
	def nosexml_plugin(self):
		class obj(object):
			pass
		from nosexml.plugin import NoseXML
		config = obj()
		config.xml_enabled = True
		config.xml_capture_stderr = True
		config.xml_formatter = self._path_to_formatter()
		plugin = NoseXML()
		plugin.configure(config, None)
		return [plugin]
	addplugins = property(nosexml_plugin)

