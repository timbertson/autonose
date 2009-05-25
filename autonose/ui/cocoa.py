import os

class Cocoa(object):
	def __init__(self, nose_args):
		nose_args += ['--xml', '--xml-formatter=nosexml.PrettyPrintFormatter']
		try:
			del os.environ['NOSE_REDNOSE']
		except KeyError: pass

	def finalize(self):
		pass
	def begin_new_run(self, current_time):
		pass


