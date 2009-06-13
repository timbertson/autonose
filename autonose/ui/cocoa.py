#!/usr/bin/env python

import sys

import os
import threading
from Cocoa import *
import cgi

from data import Data
from page import Page


class App():
	script = __file__
	def __init__(self):
		self.window = None
		self.app = NSApplication.sharedApplication()
		self.mainloop = Main(update=self.update_window, exit=self.exit)
		self.ui = threading.Thread(target=self._main)
		self.ui.start()
		def _done():
			print "UI fully loaded"
		self.mainloop.do(_done)
		self.mainloop.run()
	
	def exit(self):
		pass
		
	def update_window(self, page=None):
		if page is None:
			page = self.mainloop.page
		pass
		self.window.setPage(page.content)
	
	def _main(self):
		# self.app = wx.PySimpleApp()
		# self.frame = wx.Frame(None, wx.ID_ANY, "Autonose Report")
		# self.frame.Bind(wx.EVT_IDLE, self.mainloop.on_idle)
		# self.window = html.HtmlWindow(parent=self.frame)
		# self.update_window()
		# self.frame.Show(True)
		# self.app.MainLoop()
		print "main loop exited"

if __name__ == '__main__':
	App()
	