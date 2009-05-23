import curses

def _start():
	window = curses.initscr()
	curses.cbreak()
	curses.noecho()
	try:
		curses.start_color()
	except:
		pass
	window.keypad(1)
	return window

def _stop(window):
	window.keypad(0)
	curses.nocbreak()
	curses.echo()
	curses.endwin()

class Terminal(object):
	def __init__(self):
		self.testinfo = {}
		self.window = _start()
		self.window.insstr('hi there!', 0)
		self.window.refresh()
	
	def updateStatus(self, time):
		pass
	
	def updateTest(self, fileStamp, output):
		if fileStamp.path in self.testinfo:
			# update
			pass
	
	def finalize(self):
		_stop(self.window)
		
	
	
	#non-API methods
	def update_ui(self):
		pass
	
	def scroll_next(self):
		pass
	
	def scroll_prev(self):
		pass
	
	def scroll_top(self):
		pass
	
	def scroll_bottom(self):
		pass
		

