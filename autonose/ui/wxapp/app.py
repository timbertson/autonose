#!/usr/bin/env python

import sys

import threading
import wx
import wx.html as html
import cgi

class App():
	def __init__(self):
		self.window = None
		self.work = []
		self.lock = threading.Lock()
		self._html = '<h1>Hi!</h1>'
		
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
				print "LINE:: %r @ %s" % (line, id(line))
				self.do(lambda line=line: self.writeHTML(line))
				if not line:
					print "EOF!"
					break
		except KeyboardInterrupt:
			pass
		finally:
			self.do(self.end)
	
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
				print ">> performing: %r" % (work_item,)
				work_item()
			self.work = []
		self.lock.release()
	
	def writeHTML(self, h):
		print "setting HTML to %r @ %s" % (h,id(h))
		self._html += cgi.escape(h)
		self.window.SetPage(self._html)
	
	def _main(self):
		self.app = wx.PySimpleApp()
		self.frame = wx.Frame(None, wx.ID_ANY, "Hello World")
		self.frame.Bind(wx.EVT_IDLE, self.onIdle)
		self.window = html.HtmlWindow(parent=self.frame)
		self.window.SetPage("<html><h1>hi!</h1></html")
		self.frame.Show(True)
		self.app.MainLoop()
		print "main loop exited"

