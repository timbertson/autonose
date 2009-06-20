import cgi
from datetime import datetime
import os

h = cgi.escape

def shorten_file(file_path):
	abs_ = os.path.abspath(os.path.realpath(file_path))
	here = os.path.abspath(os.path.realpath(os.path.curdir))
	if abs_.startswith(here):
		return abs_[len(here)+1:]
	return abs_

class Summary(object):
	def __init__(self):
		self.reset()
	
	def reset(self):
		self.ran = self.failures = self.errors = 0
	
	def finish(self): pass

	def __str__(self):
		html = 'ran <span class="tests">%s tests</span>' % (self.ran,)
		if self.failures or self.errors:
			html += ' ('
			if self.failures:
				html += '<span class="failures">%s failures</span>' % (self.failures,)
				if self.errors:
					html += ", "
			if self.errors:
				html += '<span class="errors">%s errors</span>'  % (self.errors,)
			html += ')'
		return html

class Status(object):
	def __init__(self):
		self.time = None
	
	def reset(self):
		self.time = datetime.now()
		self.finish_time = None
	
	def finish(self):
		self.finish_time = datetime.now()

	def __str__(self):
		time_format = "%H:%m:%S"
		if self.time is None:
			return "loading..."
		if self.finish_time:
			diff = self.finish_time - self.time
			return 'run finished: %s (%ss)' % (self.finish_time.strftime(time_format), diff.seconds)
		return 'run started: %s' % (self.time.strftime("%H:%m:%S"),)

class Tests(object):
	def __init__(self):
		self.tests = {}
		self.finished = False
	
	def __setitem__(self, key, item):
		self.tests[key] = item
	
	def __delitem__(self, key):
		try:
			del self.tests[key]
		except KeyError:
			pass
	
	def reset(self):
		self.finished = False
		self._clear_old_tests()
		self._mark_old_tests()
	
	def finish(self):
		self.finished = True
		self._clear_old_tests()
		
	def _clear_old_tests(self):
		for test in self.tests.values():
			if test.old:
				del self.tests[test.id]
	
	def _mark_old_tests(self):
		for test in self.tests.values():
			test.old = True

	def current_tests(self):
		return [test for test in self.tests.values() if not test.old]
	
	def __str__(self):
		if self.finished and len(self.current_tests()) == 0:
			return '<h1 id="success">All tests ran successfully</h1>'
		sorted_tests = sorted(self.tests.values(), key=lambda t: t.time)
		return '\n'.join([str(test) for test in sorted_tests])
		
class Test(object):
	def __init__(self, id_, status, html):
		self.id = id_
		self.status = status
		self.html = html

		self.old = False
		self.time = datetime.now()
	
	def __str__(self):
		return """
			<div class="test %s %s">
				<h2 class="flush">%s</h2>
				%s
			</div>""" % (self.status, 'old' if self.old else 'current', self.id, self.html)

class Notice(object):
	levels = ['debug','info','error']
	def __init__(self):
		self.reset()
		
	def finish(self):
		if self.lvl == 0:
			self.val = ''

	def reset(self):
		self.val = ''
		self.lvl = 0
		
	def set(self, val, lvl=0):
		if lvl >= self.lvl:
			self.val = val
			self.lvl = lvl
	
	def __str__(self):
		return """<span class="notice %s">%s</span>""" % (self.levels[self.lvl], self.val)

class Page(object):
	def __init__(self):
		self.status = Status()
		self.summary = Summary()
		self.tests = Tests()
		self.notice = Notice()
		self.content = HtmlPage(head=self.status, foot=self.summary, body=self.tests, notice=self.notice)
	
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
		self._broadcast('reset')
	
	def _broadcast(self, methodname):
		for listener in (self.status, self.summary, self.notice, self.tests):
			getattr(listener, methodname)()
	
	def _process_results(self, attrs):
		self._broadcast('finish')
		for key in ('ran', 'failures', 'errors'):
			setattr(self.summary, key, int(attrs[key]))
	
	def _process_reports(self):
		# these appear to always be empty
		pass
	
	def _process_test(self, attrs, children=[]):
		self.summary.ran += 1
		test_id = attrs['id']
		self.notice.set("last test: %s" % (test_id,))
		status = attrs['status']
		
		if status == 'failure':
			self.summary.failures += 1
		elif status == 'error':
			self.summary.errors += 1
		elif status == 'success':
			del self.tests[test_id]
			return
		else:
			raise ValueError("unknown status type: %s" % (status,))
		
		output = []
		for child in children:
			self._process('_format_', child, lambda s: output.append(s))
		
		output.append('</div>')
		output = "\n".join(output)
		
		test = Test(test_id, attrs['status'], output)
		self.tests[test_id] = test
	
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
				<div class="line">from <code class="function">%s</code>, <a class="file" href="file://%s?line=%s">%s</a>, line <span class="lineno">%s</span>:</div>
				<div class="code"><pre>%s</pre></div>
			</li>
		""" % (attrs['function'], attrs['file'], attrs['line'], shorten_file(attrs['file']), attrs['line'], attrs['text'])
	
	def _format_cause(self, attrs, content=''):
		return """
			<li class="cause">
				<span class="type">%s</span>: <pre class="message">%s</pre>
			</li>
		""" % (attrs['type'], content)
	
	def __str__(self):
		return str(self.content)


class HtmlPage(object):
	def __init__(self, head, body, foot, notice=''):
		self.head = head
		self.body = body
		self.foot = foot
		self.notice = notice
	
	def __str__(self):
		css_path = os.path.join(os.path.dirname(__file__), 'style.css')
		return """
			<html>
				<head>
					<link rel="stylesheet" type="text/css" href="file://%s" />
				</head>
				<body>
					<div id="head" class="flush">%s</div>
					<div id="notice" class="flush">%s</div>
					<div id="tests">%s</div>
					<div id="summary" class="flush">%s</div>
				</body>
			</html>
		""" % (css_path, self.head, self.notice, self.body, self.foot)
