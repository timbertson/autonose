import cgi

class Page(object):
	def __init__(self):
		self.content = "<h1>loading...</h1>"
		self.updates = []
	
	def process_node(self, node):
		html = "<li>%s</li>\n" % (cgi.escape(repr(node)),)
		self.content += html
	
	def update_window(self, window):
		window.SetPage(self.content)
