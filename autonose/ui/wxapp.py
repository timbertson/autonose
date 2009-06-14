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
		self.lock = threading.Lock()
		self.work = []
		self.ui = threading.Thread(target=self._main)
		self.ui.start()
		def _done():
			print "UI fully loaded"
		self.do(_done)
		self.mainloop.run()
	
	def exit(self):
		def _exit():
			del self.frame
			self.app.Exit()
		self.do(_exit)
		
	def update(self, page=None):
		def _update(page):
			if page is None:
				page = self.mainloop.page
			self.window.SetPage(str(page))
		self.do(lambda: _update(page))
	
	def _main(self):
		self.app = wx.PySimpleApp()
		self.frame = wx.Frame(None, wx.ID_ANY, "Autonose Report")
		self.frame.Bind(wx.EVT_IDLE, self.on_idle)
		self.window = html.HtmlWindow(parent=self.frame)
		self.update()
		self.frame.Show(True)
		self.app.MainLoop()
		print "main loop exited"
	
	def do(self, func):
		self.lock.acquire()
		self.work.append(func)
		self.lock.release()

	def on_idle(self, *args):
		self.lock.acquire()
		if self.work:
			for work_item in self.work:
				work_item()
			self.work = []
		self.lock.release()


if __name__ == '__main__':
	App()
