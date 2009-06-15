import nosexml
import cgi
import collections
import pickle
import base64

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
	instead of xml, it just writes root-level elements to a stream
	one line at a time as base64(pickle(node))
	
	Data.decode() is responsible for reversing this process on
	the other side of the stream.
	"""
	realStream = None
	
	def __new__(cls, *a, **kw):
		if getattr(cls, 'singleton', None) is None:
			cls.singleton = super(Data, cls).__new__(cls, *a, **kw)
			cls.__init__(cls.singleton, *a, **kw)
			cls.__init__ = lambda *a, **k: None
		return cls.singleton

	def __init__(self, stream):
		self.stream = self.realStream or stream
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
			self.stream.write(self.encode(self.current))
		self.current = parent

	def characters(self,content):
		if content:
			self.current.add_content(content)

	def encode(self, elem):
		pickled = pickle.dumps(elem)
		encoded = base64.encodestring(pickled)
		# ensure no whitespace in the content (base64 does this for readability)
		encoded_single_line = ''.join(encoded.split())
		return encoded_single_line + '\n'
	
	@staticmethod
	def decode(encoded):
		decoded = base64.decodestring(encoded)
		return pickle.loads(decoded + '\n')

