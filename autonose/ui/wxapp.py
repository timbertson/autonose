#!/usr/bin/env python

import sys

import threading
import wx
import wx.html as html
import cgi

from shared import Main

class App():
	script = __file__
	def __init__(self):
		self.window = None
		self.mainloop = Main(delegate=self)
		self.ui = threading.Thread(target=self._main)
		self.ui.start()
		def _done():
			print "UI fully loaded"
		self.mainloop.do(_done)
		self.mainloop.run()
	
	def exit(self):
		del self.frame
		self.app.Exit()
		
	def update(self, page=None):
		if page is None:
			page = self.mainloop.page
		self.window.SetPage(str(page))
	
	def _main(self):
		self.app = wx.PySimpleApp()
		self.frame = wx.Frame(None, wx.ID_ANY, "Autonose Report")
		self.frame.Bind(wx.EVT_IDLE, self.mainloop.on_idle)
		self.window = html.HtmlWindow(parent=self.frame)
		self.update()
		self.frame.Show(True)
		self.app.MainLoop()
		print "main loop exited"

if __name__ == '__main__':
	App()
