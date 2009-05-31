import subprocess
import os
import sys

import logging
log = logging.getLogger(__name__)
info = log.info

import nosexml
import cgi
class XmlFormatter(object):
	realStream = None
	@classmethod
	def setRealStream(cls, stream):
		cls.realStream = stream

	def __init__(self, stream):
		self.stream = self.realStream or stream
		self.depth = 0
		self.current = None
	
	def startDocument(self):
		assert self.depth == 0, "Elements written before document started"
		self.stream.write(repr(self.stream) + '\n')
		self.stream.write( '<?xml version="1.0" encoding="UTF-8"?>\n' )
		self.stream.write( "<nosetests>\n" )

	def endDocument(self):
		assert self.depth == 0, "Not all elements where closed."
		self.stream.write( "</nosetests>\n" )

	def startElement(self,name,attrs={}):
		self._writeElement()
		self.depth += 1
		self.current = ( name, self._attrs( attrs ) )

	def endElement(self,name):
		self._writeElement( name )
		self.depth -= 1

	def characters(self,content):
		if len( content.strip() ) == 0:
			return
		self._writeElement()
		cnt = cgi.escape(content).rstrip()
		if not cnt.endswith('\n'):
			cnt += '\n'
		self.stream.write( cnt )

	def _writeElement(self,ending=None):
		if self.current and self.current[0] == ending:
			self.stream.write( "<%s%s />\n" % ( self.current[0], self.current[1] ) )
		elif self.current:
			self.stream.write( "<%s%s>\n" % ( self.current[0], self.current[1] ) )
		elif ending:
			self.stream.write( "</%s>\n" % ( ending ) )
		self.current = None

	def _attrs(self,args={}):
		return ''.join( [ ' %s="%s"' % ( k, v ) for k, v in args.iteritems() ] )
	

class AppLauncher(object):
	def __init__(self, nose_args = None):
		self.proc, self.output_stream = self.fork()
		XmlFormatter.setRealStream(self.output_stream)
		self.setup_args(nose_args)
	
	def fork(self):
		proc = subprocess.Popen(['python', __file__], stdin=subprocess.PIPE)
		return proc, proc.stdin
	
	def setup_args(self, nose_args):
		path_to_formatter_cls = __name__ + '.XmlFormatter'
		nose_args.append('--xml')
		nose_args.append('--xml-formatter=%s' % (path_to_formatter_cls,))
		try:
			del os.environ['NOSE_REDNOSE']
		except KeyError: pass

	def finalize(self):
		info("closing ui STDIN...")
		self.output_stream.close()
		info("waiting for UI to finish")
		retcode = self.proc.wait()
		info("UI finished with return code %s" % (retcode,))
		#TODO: do we care?
		# if retcode != 0:
		# 	raise RuntimeError("return code (%s) from UI is nonzero..." % (retcode,))

	def begin_new_run(self, current_time):
		self.output_stream.write('NEW RUN!\n')

if __name__ == '__main__':
	import app
	app.App()

