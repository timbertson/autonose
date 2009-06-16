#!/usr/bin/env python

import sys

import os

import cgi
import gtk
import thread
import gobject

from shared import Main

# uesful links:
# http://www.aclevername.com/articles/python-webgui/#message-passing-with-mozilla-gtkmozembed
# http://code.google.com/p/pywebkitgtk/wiki/HowDoI

class App(object):
	script = __file__
	def __init__(self):
		self.mainloop = Main(delegate=self)
		gtk.gdk.threads_init()
		thread.start_new_thread(gtk.main, ())
		self.do(self.init_gtk)
		self.mainloop.run()
	
	def exit(self):
		self.do(self._exit)
	
	def do(self, func, arg=None):
		gobject.idle_add(func, arg)
	
	def update(self, page=None):
		def _update(page=None):
			if page is None:
				page = self.mainLoop.page
			self.browser.load_html_string(str(page), "file://" + (os.path.dirname(__file__)))
		self.do(self.app.doUpdate, page)
	
	def _exit(self):
		pass
	
	def quitting(self):
		return self.quitting
	
	def quit(self):
		self.quitting = True

	def init_gtk(self, _):
		self.window = gtk.Window()
		self.window.set_title("Autonose")
		window = gtk.Window()
		box = gtk.VBox(homogeneous=False, spacing=0)
		self.browser = webkit.WebView()

		window.set_default_size(800, 600)
		window.connect('destroy', self.quit)

		window.add(box)
		box.pack_start(self.browser, expand=True, fill=True, padding=0)
		self.update("<h1>loading...</h1>")
		window.show_all()

if __name__ == '__main__':
	App()
	
