success = 'success'
fail = 'fail'
error = 'error'
skip = 'skipped'

_all_states = set([success, fail, error, skip])
_acceptable_states = set([success, skip])

class TestResultSet(object):
	"""
	a set of TestResult objects that only keeps results from the most recent set
	(i.e the only results kept are those with the newest timestamp)
	"""
	results = []
	def add(self, result):
		self._clean()
		self.results.append(result)

	def _clean(self):
		if len(self.results) == 0:
			return
		print self.results
		newest = max([result.time for result in self.results])
		self.results = filter(lambda result: result >= newest, self.results)
	
	def ok(self):
		return all([result.ok() for result in self.results])
	
	def __repr__(self): return repr(self.results)
	def __str__(self):  return str(self.results)
	
	def __eq__(self, other):
		return self.results == other.results
	def __ne__(self, other):
		return not self == other
	def __hash__(self):
		hash(self.results)
	

class TestResult(object):
	def __init__(self, state, test, err, time):
		if state not in _all_states:
			raise ValueError("state \"%s\" is invalid. Must be one of: %s" %
				(state, ', '.join(sorted(_all_states))))
		self.state = state
		self.name = str(test)
		self.time = time
		# print repr(err)
		# print '-'*80
		self.err = None if err is None else str(err)
	
	def ok(self):
		return self.state in _acceptable_states
	
	def __str__(self):
		if self.err is not None:
			return "error(%s): %s" % (type(self.err).__name__, self.err)
		return "%s: %s@%s" % (self.state, self.name, self.time)
	
	def __repr__(self):
		return "<TestResult: %s>" % (str(self),)
	
	def __eq__(self, other):
		return (self.state == other.state and
			self.name == other.name and
			self.time == other.time and
			self.err == other.err)

	def __ne__(self, other):
		return not self == other
	def __hash__(self):
		hash(self.state, self.name, self.time, self.err)
