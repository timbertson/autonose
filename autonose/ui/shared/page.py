import cgi
import time
import os

h = cgi.escape

def shorten_file(file_path):
	abs_ = os.path.abspath(os.path.realpath(file_path))
	here = os.path.abspath(os.path.realpath(os.path.curdir))
	if abs_.startswith(here):
		return abs_[len(here)+1:]
	return abs_

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
		kwargs = {}
		if node.children:
			kwargs['children'] = node.children
		if node.content:
			kwargs['content'] = node.content
		if node.attrs:
			kwargs['attrs'] = node.attrs
		result = processor(**kwargs)
		if callback is not None:
			callback(result)
		return result
		
	def process_node(self, node):
		self._process('_process_', node)
	
	def _process_new_run(self):
		self.content.clear()
		self.content.head = 'last run: %s' % (time.strftime("%H:%m:%S"),)
	
	def _process_results(self, attrs):
		html = 'ran <span class="tests">%s tests</span>' % (attrs['ran'],)
		failures = int(attrs['failures'])
		errors = int(attrs['errors'])
		
		if failures or errors:
			html += ' ('
			if failures:
				html += '<span class="failures">%s failures</span>' % (failures,)
				if errors:
					html += ", "
			if errors:
				html += '<span class="errors">%s errors</span>'  % (errors,)
			html += ')'
		self.content.foot = html
	
	def _process_reports(self):
		# these appear to always be empty
		pass
	
	def _process_test(self, attrs, children=[]):
		output = []
		output.append('<div class="test %s">' % (attrs['status'],))
		output.append('<h2 flush>%s</h2>' % (h(attrs['id']),) )
		
		for child in children:
			self._process('_format_', child, lambda s: output.append(s))
		output.append('</div>')
		self.content.tests += '\n'.join(output)
	
	def _format_traceback(self, children=[]):
		output = []
		output.append("""<ul class="traceback flush">""")
		
		for child in reversed(children):
			self._process('_format_', child, lambda s: output.append(s))
		output.append("</ul>")
		return '\n'.join(output)
	
	def _format__stream(self, name, output):
		return """
			<div class="capture %s">
				<h3>Captured %s:</h3>
				<pre>%s</pre>
			</div>""" % (name, name, output)
	
	def _format_stderr(self, content):
		return self._format__stream('stderr', content)
	
	def _format_stdout(self, content):
		return self._format__stream('stdout', content)
	
	def _format_frame(self, attrs):
		return """
			<li class="frame">
				<div class="line">from <code class="function">%s</code>, <a class="file" href="file://%s">%s</a>, line <span class="lineno">%s</span>:</div>
				<div class="code"><pre>%s</pre></div>
			</li>
		""" % tuple(map(h, (attrs['function'], attrs['file'], shorten_file(attrs['file']), attrs['line'], attrs['text'])))
	
	def _format_cause(self, attrs, content=''):
		return """
			<li class="cause">
				<span class="type">%s</span>: <pre class="message">%s</pre>
			</li>
		""" % (attrs['type'], content)
	
	def __str__(self):
		return str(self.content)


class HtmlPage(object):
	def __init__(self):
		self.clear()
	
	def clear(self):
		self.foot = ''
		self.head = ''
		self.tests = ''
	
	def __str__(self):
		css_path = os.path.join(os.path.dirname(__file__), 'style.css')
		return """
			<html>
				<head>
					<link rel="stylesheet" type="text/css" href="file://%s" />
				</head>
				<body>
					<div id="head" class="flush">%s</div>
					<div id="notice"></div>
					<div id="tests">%s</div>
					<div id="summary" class="flush">%s</div>
				</body>
			</html>
		""" % (css_path, self.head, self.tests, self.foot)
