class Node(object):
	def __init__(self, parent, name, attrs={}):
		self.parent = parent
		self.name = name
		self.attrs = attrs
		self.children = []
		self.content = ''

	def push(self, name, attrs):
		node = type(self)(self, name, attrs)
		self.children.append(node)
		return node
	
	def add_content(self, content):
		self.content += content
	
	def __getitem__(self, name):
		try:
			return self.attrs[name]
		except KeyError:
			print "WARNING: node has no key %r - discarding." % (name,)
	
	def __repr__(self):
		return '<%s: (%r) children=(%r)>\n' % (self.name, self.attrs, self.children)

class Data(object):
	"""
	The least xml-like xmlFormatter plugin you'll ever see.
	instead of xml, it just writes pickleable elements to a multiprocessing queue
	"""
	queue = None # will be set to a multiprocessing.Queue by the UI launcher
	
	#def __new__(cls, *a, **kw):
	#	if getattr(cls, 'singleton', None) is None:
	#		cls.singleton = super(Data, cls).__new__(cls)
	#		cls.__init__(cls.singleton, *a, **kw)
	#		cls.__init__ = lambda *a, **k: None
	#	return cls.singleton

	def __init__(self, stream):
		assert self.queue is not None, "queue has not been set on Data"
		self.depth = 0
		self.root = Node(None, 'root')
		self.current = self.root
	
	def startDocument(self):
		assert self.current is self.root, "Elements written before document started"
		self.startElement('new_run')
		self.endElement()

	def endDocument(self):
		assert self.current is self.root, "Not all elements were closed."

	def startElement(self, name, attrs={}):
		self.current = self.current.push(name, attrs)

	def endElement(self, name=None):
		parent = self.current.parent
		if parent is self.root:
			self.queue.put(self.current)
		self.current = parent

	def characters(self,content):
		if content:
			self.current.add_content(content)


