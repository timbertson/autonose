import curses
import sys
import time

import os
import termstyle

import sys

_logfile = open('.curses-log','w')
def log(s):
	_logfile.write(s + '\n')

class obj(object): pass
col = obj()
col.transparent = -1
def init_colors():
	global col
	i = 0
	cols = {
		'red':curses.COLOR_RED,
		'green':curses.COLOR_GREEN,
		'blue':curses.COLOR_BLUE,
		'black': curses.COLOR_BLACK,
		'yellow': curses.COLOR_YELLOW,
		'cyan': curses.COLOR_CYAN,
		'magenta': curses.COLOR_MAGENTA,
		'white': curses.COLOR_WHITE,
	}
	for name, fg in cols.items():
		curses.init_pair(i, fg, col.transparent)
		setattr(col, name, i)
		i += 1
		if i > curses.COLORS:
			raise RuntimeError(
				"not enough colours! (wanted %s, but there are only %s available)" %
				(len(cols), curses.COLORS))
	
def _start():
	window = curses.initscr()
	curses.start_color()
	curses.use_default_colors()
	init_colors()
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
			log("writeln_map: %r" % (self._line.splitlines(),))
			map(self.proxy.writeln, self._line.splitlines())
			self._line = ''
	
	def writeln(self, s=''):
		log('writeln: %r' % (s))
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
		self.window.addstr(self.current_line, 0, s, curses.color_pair(col.green))
		self.current_line += 1
		self._redraw()
	
	def finalize(self):
		time.sleep(1)
		_stop(self.window)
		_logfile.close()
	
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
		

