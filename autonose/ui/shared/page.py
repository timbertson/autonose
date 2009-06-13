import cgi
import time
import os

h = cgi.escape


class Page(object):
	def __init__(self):
		self.content = HtmlPage()
		self.content.head = '<h1>loading!</h1>'
		self.updates = []
	
	def _process(self, prefix, node, callback = None):
		try:
			processor = getattr(self, prefix + str(node.name))
		except AttributeError, e:
			print "Error processing results: %s" % (e.message,)
			return None
		result = processor(node.attrs, node.children)
		if callback is not None:
			callback(result)
		return result
		
	def process_node(self, node):
		self._process('_process_', node)
	
	def _process_new_run(self, attrs, children):
		assert len(children) == 0, "unexpected children"
		self.content.clear()
		self.content.head = 'last run: %s' % (time.strftime("%H:%m:%S"),)
	
	def _process_results(self, attrs, children):
		html = 'ran %s tests (%s failures, %s errors)' % (attrs['ran'], attrs['failures'], attrs['errors'])
		assert len(children) == 0, "unexpected children"
		self.content.foot = html
	
	def _process_reports(self, attrs, children):
		pass
	
	def _process_test(self, attrs, children):
		self.content.tests += "%s<br />" % (h(repr(attrs)),)
		output = []
		for child in children:
			self._process('_format_', child, lambda s: output.append(s))
		self.content.tests += '<br />\n'.join(output)
	
	def _format_traceback(self, attrs, children):
		output = []
		for child in children:
			self._process('_format_', child, lambda s: output.append(s))
		return ''.join(output)
	
	def _format_stderr(self, attrs, children):
		return "STDERR: " + repr(attrs)
	
	def _format_frame(self, attrs, children):
		return "FRAME: " + repr(attrs)
	
	def _format_cause(self, attrs, children):
		return "CAUSE: " + repr(attrs)
	
	def __str__(self):
		return str(self.content)


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
