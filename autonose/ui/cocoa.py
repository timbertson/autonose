#!/usr/bin/env python

import sys
import time
import os
import threading
from Cocoa import *
from WebKit import WebView
import cgi
import objc

from shared import Main
from cocoa_util import ScrollKeeper

class AutonoseApp(NSObject):
	def initWithMainLoop_(self, mainLoop):
		self.init()
		self.mainLoop = mainLoop
		self.scroll_keeper = None
		return self
		
	def run(self):
		self.app = NSApplication.sharedApplication()
		origin = [100,200]
		size = [800,600]
		self.view = WebView.alloc().initWithFrame_frameName_groupName_(NSMakeRect(0,0, *size), None, None)
		self.view.setAutoresizingMask_(NSViewHeightSizable | NSViewWidthSizable)
		
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
	
	def runMainLoop(self):
		self.releasePool = NSAutoreleasePool.alloc().init()
		self.mainLoop.run()
		self.releasePool.release()


class App(object):
	script = __file__
	def __init__(self):
		self.mainloop = Main(delegate=self)
		self.app = AutonoseApp.alloc().initWithMainLoop_(self.mainloop)
		sel = objc.selector(self.app.runMainLoop, signature="v@:")
		self.main = NSThread.detachNewThreadSelector_toTarget_withObject_(sel, self.app, None)
		self.app.run()
	
	def exit(self):
		self.do(self.app.doExit)
	
	def do(self, func, arg=None):
		sel = objc.selector(func, signature="v@:")
		self.app.performSelectorOnMainThread_withObject_waitUntilDone_(sel, arg, False)
	
	def update(self, page=None):
		f = open('/tmp/html.html', 'w')
		f.write(str(page))
		f.close()
		
		self.do(self.app.doUpdate, str(page))


if __name__ == '__main__':
	App()
	