#!/usr/bin/env python

import os
import threading
import wx
import wx.html as html
import subprocess
import time
import sys
import cgi

from StringIO import StringIO

from base import BaseUI

class PipeWrapper(object):
	# unittest calls println, which is not defined on a
	# subprocess.PIPE-created file stream. so we wrap it...
	def __init__(self, wrapped):
		self.wrapped = wrapped
	
	def write(self, *s):
		print >> sys.stder, "WRITING: %r" % (s)
		self.wrapped.write(*s)

	def writeln(self, *s):
		self.writelines(s)
		
	def __getattr__(self, attr):
		return getattr(self.wrapped, attr)

class WxAppSpawner(BaseUI):
	def __init__(self, nose_args = None):
		self.setup_args(nose_args)
		self.proc = self.fork()
	
	def fork(self):
		proc = subprocess.Popen(['python', __file__], stdin=subprocess.PIPE)
		self.output_stream = PipeWrapper(proc.stdin)
		return proc
	
	def setup_args(self, nose_args):
		nose_args += ['--xml', '--xml-formatter=nosexml.PrettyPrintFormatter']
		try:
			del os.environ['NOSE_REDNOSE']
		except KeyError: pass

	def finalize(self):
		print "closing ui STDIN..."
		self.output_stream.close()
		print self.output_stream.closed
		print "waiting for UI to finish"
		retcode = self.proc.wait()
		if retcode != 0:
			print "WARNING: return code (%s) is nonzero..." % (retcode,)
			return False
		return True

	def begin_new_run(self, current_time):
		self.output_stream.writeln('NEW RUN!')


class WxApp(BaseUI):
	def __init__(self):
		self.window = None
		self.work = []
		self.lock = threading.Lock()

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
				print repr(line)
				if not line:
					break
				self.do(lambda: self.writeHTML(cgi.escape(line)))
		except KeyboardInterrupt:
			pass
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
				work_item()
			self.work = []
		self.lock.release()
	
	def writeHTML(self, h):
		print "setting HTML to %s" % h
		if self.window:
			self.window.SetPage(h)
	
	def _main(self):
		self.app = wx.PySimpleApp()
		self.frame = wx.Frame(None, wx.ID_ANY, "Hello World")
		self.frame.Bind(wx.EVT_IDLE, self.onIdle)
		self.window = html.HtmlWindow(parent=self.frame)
		self.window.SetPage("<html><h1>hi!</h1></html")
		self.frame.Show(True)
		self.app.MainLoop()
		print "main loop exited"

if __name__ == '__main__':
	print "starting UI in new process..."
	WxApp()

