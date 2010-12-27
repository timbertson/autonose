success = 'success'
fail = 'fail'
error = 'error'
skip = 'skipped'

_all_states = set([success, fail, error, skip])
_acceptable_states = set([success, skip])

import logging
import traceback
import itertools
log = logging.getLogger(__name__)

class ResultEvent(object): pass

class TestResultSet(object):
	"""
	a set of TestResult objects that only keeps results from the most recent set
	(i.e the only results kept are those with the newest timestamp)
	"""
	def __init__(self):
		self.results = []
		
	def add(self, result):
		self.results.append(result)
		self._clean()

	def _clean(self):
		if len(self.results) <= 1:
			return
		newest = max([result.time for result in self.results])
		self.results = filter(lambda result: result.time >= newest, self.results)
	
	def ok(self):
		return all([result.ok() for result in self.results])
	
	def __repr__(self):
		repr(self.results)
		results = self.results
		if results:
			results = "\n   " + "\n   ".join(map(repr, results))
		return "<TestResults [%s]: %s>" % ("ok" if self.ok() else "NOT OK", results)

	def __str__(self):  return str(self.results)
	
	def __eq__(self, other):
		return type(self) == type(other) and self.results == other.results
	def __ne__(self, other):
		return not self == other
	def __hash__(self):
		hash(self.results)

class TestResult(ResultEvent):
	def __init__(self, state, id, name, address, path, err, run_start, outputs):
		if state not in _all_states:
			raise ValueError("state \"%s\" is invalid. Must be one of: %s" %
				(state, ', '.join(sorted(_all_states))))
		self.id = id
		self.state = state
		self.name = name
		self.time = run_start
		self.path = path
		self.outputs = outputs
		self.address = address
		if err:
			self.outputs.insert(0, ('traceback', self.extract_error(err)))
		self.attrs = ['id','state','name','time','path','address']
	
	def extract_error(self, err):
		cls, instance, tb = err
		trace = traceback.extract_tb(tb)
		message = str(instance)
		marker = "begin captured"
		if marker in message:
			lines = message.splitlines()
			lines = itertools.takewhile(lambda line: marker not in line, lines)
			message = "\n".join(lines)
		return (cls, message, trace)

	def ok(self):
		return self.state in _acceptable_states
	
	def __str__(self):
		return "%s: %s@%s" % (self.state, self.name, self.time)
	
	def __repr__(self):
		return "<TestResult: %s>" % (str(self),)
	
	def __eq__(self, other):
		if not type(self) == type(other): return False
		get_self = lambda a: getattr(self, a)
		get_other = lambda a: getattr(other, a)
		return map(get_self, self.attrs) == map(get_other, self.attrs)

	def __ne__(self, other):
		return not self == other
	def __hash__(self):
		hash(self.state, self.name, self.time, self.err)
	
	def affect_state(self, state):
		state[self.path].test_results.add(self)
	
	@property
	def runnable_address(self):
		# no idea if this will work for all addresses,
		# it seems like a roundabout way to get back to
		# a particular test...
		log.warn(repr(self.address))
		return ":".join(map(str, self.address[1:]))

	def affect_page(self, page):
		page.test_complete(self)
