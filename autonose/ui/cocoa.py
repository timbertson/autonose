#!/usr/bin/env python

import sys
import time
import os
import threading
from Cocoa import *
from WebKit import WebView
import cgi
import objc
import subprocess
import cgi

from shared import Main
from cocoa_util.scroll_keeper import ScrollKeeper

VOID = "v@:"


class AutonoseApp(NSObject):
	def initWithMainLoop_(self, mainLoop):
		self.init()
		self._init_file_openers()
		self.mainLoop = mainLoop
		self.scroll_keeper = None
		return self
	
	def _init_file_openers(self):
		self.file_openers = [TextMateOpener(), DefaultOpener()]

	def run(self):
		self.app = NSApplication.sharedApplication()
		
		nib = NSNib.alloc().initWithContentsOfURL_(NSURL.fileURLWithPath_(os.path.dirname(__file__) + '/cocoa_util/MainMenu.nib'))
		nib.instantiateNibWithOwner_topLevelObjects_(self, None)
		
		origin = [100,200]
		size = [800,600]
		self.view = WebView.alloc().initWithFrame_frameName_groupName_(NSMakeRect(0,0, *size), None, None)
		self.view.setAutoresizingMask_(NSViewHeightSizable | NSViewWidthSizable)
		self.view.setPolicyDelegate_(self)
		
		self.htmlView = self.view.mainFrame()
		self.scroll_keeper = ScrollKeeper(self.htmlView)
		self.view.setFrameLoadDelegate_(self)
		window_mask = NSTitledWindowMask | NSResizableWindowMask | NSClosableWindowMask | NSMiniaturizableWindowMask
		window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
			NSMakeRect(*(origin + size)), window_mask, NSBackingStoreBuffered, True)
		window.setTitle_("Autonose")
		self.doUpdate("<h1>loading...</h1>")
		
		window.contentView().addSubview_(self.view)
		window.makeKeyAndOrderFront_(None)
		self.app.activateIgnoringOtherApps_(True)
		try:
			self.app.run()
		except KeyboardInterrupt:
			self.doExit()
	
	def doExit(self, *args):
		self.app.terminate_(self)

	def doUpdate(self, page=None):
		if page is None:
			page = self.mainLoop.page
		if self.scroll_keeper: self.scroll_keeper.save()
		self.htmlView.loadHTMLString_baseURL_(str(page), NSURL.fileURLWithPath_(os.path.dirname(__file__)))
		self.htmlView.webView().setNeedsDisplay_(True)
	
	def webView_didFinishLoadForFrame_(self,view, frame):
		if self.scroll_keeper: self.scroll_keeper.restore()
	
	def webView_decidePolicyForNavigationAction_request_frame_decisionListener_(self, view, action_info, request, frame, listener):
		path = request.URL().path()
		url = request.URL().absoluteString()
		lineno = 0
		if '?' in url:
			try:
				param_str = url.split('?')[-1]
				params = cgi.parse_qs(param_str)
				lineno = params['line'][0]
			except (IndexError, KeyError):
				pass
		if path.endswith('.py'):
			for opener in self.file_openers:
				if opener.open(path, lineno): break # it's assumed that the last (default) opener will never fail
			listener.ignore()
		else:
			listener.use()
	
	def runMainLoop(self):
		self.releasePool = NSAutoreleasePool.alloc().init()
		self.mainLoop.run()
		self.releasePool.release()

class TextMateOpener(object):
	def __init__(self):
		#FIXME: very dodgy...
		self.tm_path = '/Applications/TextMate.app/Contents/Resources/mate'
		self.has_tm = os.path.isfile(self.tm_path)
	
	def open(self, path, line):
		if not self.has_tm:
			return False
		print line
		subprocess.Popen([self.tm_path, path, '-wl', str(line)])
		return True

class DefaultOpener(object):
	def open(self, path, line):
		from Cocoa import NSWorkspace
		NSWorkspace.sharedWorkspace().openFile_(path)
		return True

class App(object):
	script = __file__
	def __init__(self):
		self.mainloop = Main(delegate=self)
		self.app = AutonoseApp.alloc().initWithMainLoop_(self.mainloop)
		sel = objc.selector(self.app.runMainLoop, signature=VOID)
		self.main = NSThread.detachNewThreadSelector_toTarget_withObject_(sel, self.app, None)
		self.app.run()
	
	def exit(self):
		self.do(self.app.doExit)
	
	def do(self, func, arg=None):
		sel = objc.selector(func, signature=VOID)
		self.app.performSelectorOnMainThread_withObject_waitUntilDone_(sel, arg, False)
	
	def update(self, page=None):
		f = open('/tmp/html.html', 'w')
		f.write(str(page))
		f.close()
		
		self.do(self.app.doUpdate, str(page))


if __name__ == '__main__':
	App()
	