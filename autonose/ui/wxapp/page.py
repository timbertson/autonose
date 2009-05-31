import cgi
import time
import os

h = cgi.escape

class Page(object):
	def __init__(self):
		self.content = HtmlPage()
		self.content.head = '<h1>loading!</h1>'
		self.updates = []
	
	def process_node(self, node):
		action = getattr(self, "_process_%s" % (node.name), None)
		if action is None:
			print "Can't process event: %s" % (node.name,)
			return
		action(node.attrs, node.children)
	
	def update_window(self, window):
		window.SetPage(str(self.content))
	
	def _process_new_run(self, attrs, children):
		print "new run!"
		self.content.clear()
		self.content.head = 'last run: %s' % (time.strftime("%H:%m:%S"),)
	
	def _process_results(self, attrs, children):
		html = 'ran %s tests (%s failures, %s errors)' % (attrs['ran'], attrs['failures'], attrs['errors'])
		self.content.foot = html
	
	def _process_reports(self, attrs, children):
		"""process reports of failed tests"""
		self.content.body += "<li>%s</li>" % (h(repr(children)),)
	
	def _process_test(self, attrs, children):
		self.content.tests += "%s<br />" % (h(repr(attrs)),)

class HtmlPage(object):
	def __init__(self):
		self.clear()
	
	def clear(self):
		self.foot = ''
		self.head = ''
		self.tests = ''
		self.body = ''
	
	def __str__(self):
		css_path = os.path.join(os.path.dirname(__file__), 'style.css')
		return """
			<html>
				<head>
					<link rel="stylesheet" type="text/css" href="file://%s" />
				</head>
				<body>
					<div id="head">%s</div>
					<hr />
					<div id="tests">%s</div>
					<hr />
					<div id="content">%s</div>
					<hr />
					<div id="summary">%s</div>
				</body>
			</html>
		""" % (css_path, self.head, self.tests, self.body, self.foot)
