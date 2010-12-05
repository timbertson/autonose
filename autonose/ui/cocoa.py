#!/usr/bin/env python

import sys
import time
import os
import threading
import logging
log = logging.getLogger(__name__)
try:
	from Cocoa import *
	from WebKit import WebView
	import cgi
	import objc
	import subprocess
	import cgi

	from shared import Main
	from shared import urlparse
	from shared.ipc import IPC
	from cocoa_util.scroll_keeper import ScrollKeeper
	from cocoa_util.file_openers import all_openers

	VOID = "v@:"

	debug = log.debug
	info = log.info

	class AutonoseApp(NSObject):
		def initWithMainLoop_runner_(self, mainLoop, runner):
			self.init()
			self.runner = runner
			self._init_file_openers()
			self.mainLoop = mainLoop
			self.scroll_keeper = None
			return self
		
		def _init_file_openers(self):
			instantiate = lambda cls: cls()
			self.file_openers = map(instantiate, all_openers)

		def run(self):
			self.app = NSApplication.sharedApplication()
			self.app.setDelegate_(self)
			
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
			self.runner = None # when doExit() is called, the main runner is already ending
			self.app.terminate_(self)
		
		def applicationWillTerminate_(self, sender):
			if self.runner:
				self.runner.terminate()
		
		def doUpdate(self, page=None):
			if page is None:
				page = self.mainLoop.page
			if self.scroll_keeper: self.scroll_keeper.save()
			self.htmlView.loadHTMLString_baseURL_(str(page), NSURL.fileURLWithPath_(os.path.dirname(__file__)))
			self.htmlView.webView().setNeedsDisplay_(True)
		
		def webView_didFinishLoadForFrame_(self,view, frame):
			if self.scroll_keeper: self.scroll_keeper.restore()
		
		def webView_decidePolicyForNavigationAction_request_frame_decisionListener_(self, view, action_info, request, frame, listener):
			url = request.URL().absoluteString()
			if urlparse.editable_file(url):
				path, line = urlparse.path_and_line_from(url)
				self._open_source_file(path, line)
				listener.ignore()
			else:
				listener.use()
		
		def _open_source_file(self, path, line):
			for opener in self.file_openers:
				if opener.open(path, line): break # it's assumed that the last (default) opener will never fail
		
		def runMainLoop(self):
			self.releasePool = NSAutoreleasePool.alloc().init()
			self.mainLoop.run()
			self.releasePool.release()

	class App(object):
		script = __file__
		def __init__(self, main_ipc):
			self.mainloop = Main(delegate=self, queue=main_ipc.queue)
			self.app = AutonoseApp.alloc().initWithMainLoop_runner_(self.mainloop, main_ipc)
			sel = objc.selector(self.app.runMainLoop, signature=VOID)
			self.main = NSThread.detachNewThreadSelector_toTarget_withObject_(sel, self.app, None)
			self.app.run()
		
		def exit(self):
			self.do(self.app.doExit)
		
		def do(self, func, arg=None):
			sel = objc.selector(func, signature=VOID)
			self.app.performSelectorOnMainThread_withObject_waitUntilDone_(sel, arg, False)
		
		def update(self, page=None):
			self.do(self.app.doUpdate, str(page))

except ImportError:
	log.warn("Warning: couldn't import Cocoa")
