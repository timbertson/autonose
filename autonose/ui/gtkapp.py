#!/usr/bin/env python

import sys
import os
import cgi
import thread
import subprocess

import gtk
import webkit
import gobject
import logging
log = logging.getLogger(__name__)

from shared import urlparse


class App(object):
	script = __file__
	URI_BASE = "file://" + (os.path.dirname(__file__))
	def __init__(self, mainloop):
		self.quitting = False
		self.mainloop = mainloop
		gtk.gdk.threads_init()
		thread.start_new_thread(gtk.main, ())
		self.do(self.init_gtk)
	
	def exit(self): # called by main thread
		if self.quitting:
			return # we already know!
		self.do(self.quit)
		self.do(lambda _=None: gtk.main_quit())
	
	def do(self, func, arg=None):
		gobject.idle_add(func, arg)
	
	def update(self, page=None):
		def _update(page=None):
			if page is None:
				page = self.mainLoop.page
			self.browser.load_html_string(str(page), self.URI_BASE)
		self.do(_update, page)
	
	def _navigation_requested_cb(self, view, frame, networkRequest):
		url = networkRequest.get_uri()
		if url.startswith(self.URI_BASE + "#"):
			test_id = url.split('#',1)[1]
			self.mainloop.run_just(test_id)
			return 1
		opener = os.environ.get('EDITOR', 'gnome-open')
		#log.info("navigation requested: %s" % (url,))
		if not urlparse.editable_file(url):
			return 0
		path, line = urlparse.path_and_line_from(url)
		subprocess.Popen([opener, path])
		# return 1 to stop any other handlers running
		return 1

	def quit(self, _=None):
		self.quitting = True
		self.mainloop.terminate()

	def init_gtk(self, _):
		self.window = gtk.Window()
		self.window.set_title("Autonose")
		
		scrollView = gtk.ScrolledWindow()
		self.browser = webkit.WebView()
		self.browser.connect('navigation_requested', self._navigation_requested_cb)
		scrollView.add(self.browser)

		self.window.set_default_size(800, 600)
		self.window.connect('destroy', self.quit)

		self.window.add(scrollView)
		self.update("<h1>loading...</h1>")
		self.window.show_all()

