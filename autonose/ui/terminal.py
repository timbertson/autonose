import curses
import sys
import time

import os
import termstyle

import sys

def _start():
	window = curses.initscr()
	curses.cbreak()
	curses.noecho()
	window.keypad(1)
	return window

def _stop(window):
	window.keypad(0)
	curses.nocbreak()
	curses.echo()
	curses.endwin()

class OutputProxy(object):
	def __init__(self, proxy):
		self.proxy = proxy
		self._line = ''
	
	def write(self, s):
		self._line += s
		if '\n' in self._line:
			map(self.proxy.writeln, self._line.split('\n'))
			self._line = ''
	
	def writeln(self, s=''):
		if not s.endswith('\n'):
			s = s + '\n'
		self.write(s)
	
	def __getattr__(self, attr):
		return DoNothing()

class DoNothing(object):
	def __nonzero__(self): return False
	def __call__(self, *args): pass

class Terminal(object):
	def __init__(self):
		sys.stdout = sys.stderr = OutputProxy(self)
		self._logfile = open('.curses-log','w')
		self.last_run_time = time.localtime()
		self.testinfo = {}
		self.window = _start()
		self.current_line = 0
		self._size()
		self._redraw()

	def begin_new_run(self, current_time=None):
		if current_time is None:
			current_time = self.last_run_time
		else:
			self.last_run_time = current_time
		self.status.erase()
		self.status.bkgd(' ', curses.A_REVERSE | curses.A_BOLD)
		self.status.insstr("Run started at: %s  " % (time.strftime("%H:%m:%S", self.last_run_time)), 0)
		self.window.refresh()
	
	def update_test(self, fileStamp, output):
		if fileStamp.path in self.testinfo:
			# update
			pass
	
	def writeln(self, s):
		self.window.addstr(self.current_line, 0, s)
		self._logfile.write(s + '\n')
		self.current_line += 1
		self._redraw()
	
	def finalize(self):
		_stop(self.window)
		self._logfile.close()
	
	#non-API methods
	
	def _resize(self):
		self.status.erase()
		self.window.erase()
		self._size()
		self._redraw()
	
	def _redraw(self):
		self.begin_new_run()
		self.window.refresh()
		
	def _size(self):
		height, width = self.window.getmaxyx()
		self.status = self.window.subwin(1, 0, height-1, 0)
	
	def scroll_next(self):
		pass
	
	def scroll_prev(self):
		pass
	
	def scroll_top(self):
		pass
	
	def scroll_bottom(self):
		pass
		

