"""
Copyright (c) 2008 Paul Davis <paul.joseph.davis@gmail.com>

This file is part of nosexml, which is released under the MIT license.
"""

from formatter import XMLFormatter

class PrettyPrintFormatter(XMLFormatter):
    """Pretty-Print XML event formatter.
    
        This class is the default NoseXML output style and presents a basic
        pretty printed output for Nosetests.
    """
    def __init__(self,stream):
        self.indent = '    '
        self.depth = 0
        self.stream = stream
        self.current = None

    def setStream(self,stream):
        self.stream = stream

    def startDocument(self):
        assert self.depth == 0, "Elements written before document started"
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
        cnt = content.replace( '&', '&amp;' ).replace( '<', '&lt;' ).replace( '>', '&gt;' ).rstrip()
        if cnt[-1:] != '\n':
            cnt = '%s\n' % cnt
        self.stream.write( '%s%s' % ( self.indent * ( self.depth + 1 ), cnt ) )

    def _writeElement(self,ending=None):
        if self.current and self.current[0] == ending:
            self.stream.write( "%s<%s%s />\n" % ( self.indent * self.depth, self.current[0], self.current[1] ) )
        elif self.current:
            self.stream.write( "%s<%s%s>\n" % ( self.indent * self.depth, self.current[0], self.current[1] ) )
        elif ending:
            self.stream.write( "%s</%s>\n" % ( self.indent * self.depth, ending ) )
        self.current = None

    def _attrs(self,args={}):
        return ''.join( [ ' %s="%s"' % ( k, v ) for k, v in args.iteritems() ] )