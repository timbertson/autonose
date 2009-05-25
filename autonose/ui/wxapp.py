import os
import threading
import wx



class WxApp(object):
	def __init__(self, nose_args):
		self.setup_args(nose_args)
		threading.Thread(target=self._main).start()
	
	def _main(self):
		self.app = wx.PySimpleApp()
		frame = wx.Frame(None, wx.ID_ANY, "Hello World")
		frame.Show(True)
		self.app.MainLoop()
	
	def setup_args(self, nose_args):
		nose_args += ['--xml', '--xml-formatter=nosexml.PrettyPrintFormatter']
		try:
			del os.environ['NOSE_REDNOSE']
		except KeyError: pass

	def finalize(self):
		pass

	def begin_new_run(self, current_time):
		pass


