#!/usr/bin/env python

import sys

import os
import threading
from Cocoa import *
from WebKit import WebView
import cgi
from shared import Main

class CocoaLock(object):
	def __init__(self):
		lock = NSLock.alloc().init()
		self.acquire = lock.lock
		self.release = lock.unlock

import objc
class App():
	script = __file__
	def __init__(self):
		self.window = None
		self.mainloop = Main(delegate=self)
		self.lock = CocoaLock()
		self.mainloop = Main(delegate=self, lock=self.lock)
		self.main = NSThread.detachNewThreadSelector_toTarget_withObject_(self.runMainLoop.sel, self, None)
		
		def _done():
			print "MAIN fully loaded"
		self.mainloop.do(_done)
		self._main()
	
	def exit(self):
		pass
	
	def runMainLoop(self):
		self.releasePool = NSAutoreleasePool.alloc().init()
		self.mainloop.run()
	runMainLoop.sel = objc.selector(runMainLoop, signature="v@:")
	
	def update(self, page=None):
		self.releasePool.drain()
		if page is None:
			page = self.mainloop.page
	
	def _main(self):
		self.app = NSApplication.sharedApplication()
		rect = NSMakeRect(0,100,200,200)
		htmlView = WebView.alloc().initWithFrame_frameName_groupName_(rect, None, None)
		self.view = htmlView.mainFrame()
		window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
			rect, NSTitledWindowMask | NSResizableWindowMask, NSBackingStoreBuffered, True)
		
		window.setTitle_("test1")
		
		self.view.loadHTMLString_baseURL_("hi!", NSURL.fileURLWithPath_(os.path.dirname(__file__)))
		window.contentView().addSubview_(htmlView)
		window.makeKeyAndOrderFront_(None)
    
		self.app.run()

		print "main loop exited"

if __name__ == '__main__':
	App()
	