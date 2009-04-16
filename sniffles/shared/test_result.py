
class _state(object):
	def __init__(self, description):
		self.description = description
	def __str__(self):  return str(self.description)
	def __repr__(self): return repr(self.description)

success = _state('success')
fail = _state('fail')
error = _state('error')
skip = _state('skipped')

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
		map(lambda x: x.time, self.results)
		
		newest = max([result.time for result in self.results])
		self.results = filter(lambda result: result.time >= newest, self.results)
	
	def __repr__(self): return repr(self.results)
	def __str__(self):  return str(self.results)
	

class TestResult(object):
	def __init__(self, state, test, err, time):
		if state not in _all_states:
			raise ValueError("state must be one of: %s" % (_all_states,))
		self.state = state
		self.name = str(test)
		self.time = time
		self.err = err
		print(err)
	
	def ok(self):
		self.state in _acceptable_states
	
	def __str__(self):
		if self.err:
			return str(self.err)
		return "%s: %s@%s" % (self.state, self.name, self.time)
	
	def __repr__(self):
		return "<TestResult: %s>" % (str(self),)
