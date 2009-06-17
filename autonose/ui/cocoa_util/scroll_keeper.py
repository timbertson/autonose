import time
from Cocoa import *

# this class is far more involved than it ought to be.
# all it does is make sure the WebView scroll position is maintained
# across page updates

# we need a 1 second wait before we'll believe a scroll position of (0,0)
# to be the truth, because there are many times when the scroll pos has
# been set to nonzero but the following update will still see (0,0)

class ScrollKeeper(object):
	def __init__(self, html_view):
		self.html_view = html_view
		self.last_update = time.time()
		self.pos = NSMakePoint(0,0)
		self.needs_scroll = False
	
	def _scroll_view(self):
		return self.html_view.frameView().documentView().enclosingScrollView()
	def _scroll_source(self):
		return self._scroll_view().contentView() 
	def _scroll_target(self):
		return self._scroll_view().documentView()
	
	def save(self):
		if self.needs_scroll:
			return # we've already saved a position
		pos = self._scroll_source().bounds().origin
		if not self._spurious(pos):
			self.pos = pos
			self.needs_scroll = True
	
	def _spurious(self, pos):
		default_scroll = (pos.y == pos.x == 0)
		old = self.last_update < time.time() - 1
		return default_scroll and not old

	def restore(self):
		self.last_update = time.time()
		self._scroll_target().scrollPoint_(self.pos)
		self.needs_scroll = False

