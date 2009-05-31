#!/usr/bin/env python

import sys

import threading
import wx
import wx.html as html
import cgi

from data import Data
from page import Page

class App():
	def __init__(self):
		self.window = None
		self.work = []
		self.lock = threading.Lock()
		self.page = Page()
		
		self.ui = threading.Thread(target=self._main)
		self.ui.start()
		def _done():
			print "UI fully loaded"
		self.do(_done)
		self.input_loop()
	
	def input_loop(self):
		try:
			while not sys.stdin.closed:
				line = sys.stdin.readline()
				self.process_line(line)
				if not line:
					print "UI received EOF"
					break
		except KeyboardInterrupt:
			pass
		finally:
			self.do(self.end)
	
	def process_line(self, line):
		node = Data.decode(line)
		self.page.process_node(node)
		self.do(lambda: self.page.update_window(self.window))
	
	def end(self):
		del self.frame
		self.app.Exit()
	
	def do(self, func):
		self.lock.acquire()
		self.work.append(func)
		self.lock.release()
	
	def onIdle(self, something_else = None):
		self.lock.acquire()
		if self.work:
			for work_item in self.work:
				work_item()
			self.work = []
		self.lock.release()
	
	def _main(self):
		self.app = wx.PySimpleApp()
		self.frame = wx.Frame(None, wx.ID_ANY, "Autonose Report")
		self.frame.Bind(wx.EVT_IDLE, self.onIdle)
		self.window = html.HtmlWindow(parent=self.frame)
		self.page.update_window(self.window)
		self.frame.Show(True)
		self.app.MainLoop()
		print "main loop exited"

