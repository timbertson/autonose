"""A plugin for nosetests to write output in XML

Copyright (c) 2008 Paul Davis <paul.joseph.davis@gmail.com>

This file is part of nosexml, which is released under the MIT license.
"""

import logging
import os
import re
import sys
import unittest
import linecache

from cStringIO import StringIO

import nose

log = logging.getLogger( __name__ )

class NullRedirect(object):
    """Redirects all other output into the ether.
    """
    def __init__(self):
        self.buf = StringIO()
    def write(self,mesg):
        self.buf.write( mesg )
    def writeln(self,*args):
        if len( args ) > 0:
            self.buf.write( '%s\n' % args )
        else:
            self.buf.write( '\n' )

class NoseXML(nose.plugins.base.Plugin):
    """Write Nosetests output in XML
    
        This version of the XML plugin is based on issue140_ on the nosetests
        Google Code site.
        
        .. _issue140: http://code.google.com/p/python-nose/issues/detail?id=140

        Instead of directly creating an XML DOM document and then using classes
        to render the DOM, I opted to go with a more stream oriented output
        using a SAX style writer. Classes that wish to format output to their
        liking should create a class that inherits from XMLFormatter and pass
        the full module and class name as a python path to the --xml-formatter
        command line argument.
        
        Command line arguments:
        
        --xml                           Enable the XML output plugin.
        --xml-formatter=XML_FORMATTER   Provide a class to format the XML
                                        SAX events into the desired format.
                                        Defaults to nosexml.PrettyPrintFormatter.
        --xml-no-stderr                 Disable capturing of stderr. This can be
                                        extremely useful when an error is causing
                                        the system to exit without displaying an
                                        exception traceback.
    """
    name = 'nose-xml'
    enabled = False
    score = 499 #Just trump the capture plugin.
    
    def __init__(self):
        # Keep original stderr around for debugging
        sys.debug = sys.stderr
        self.capture_stderr = True
        self.stringio = StringIO
        self.sys = sys
        self.stdout = []
        self.outbuf = None
        self.stderr = []
        self.errbuf = None
        self.redirect = NullRedirect()
        self.ran = 0
        self.errors = 0
        self.failures = 0
        self.escapes = [
            ( re.compile( r'&' ), '&amp;' ),
            ( re.compile( r'"' ), '&quot;' ),
            ( re.compile( r"'" ), '&apos;' ),
            ( re.compile( r'<' ), '&lt;' ),
            ( re.compile( r'>' ), '&gt;' )
        ]
    
    def options(self,parser,env=os.environ):
        parser.add_option( '--xml', dest='xml_enabled', default=False,
            action="store_true", help="Format output as an XML document.")
        parser.add_option( '--xml-formatter', dest='xml_formatter',
            default='nosexml.PrettyPrintFormatter',
            help="Class that will process the xml document for output." \
                    " The default is to use nosexml.PrettyPrintFormatter" \
                    " which will write the xml document as plain text." )
        parser.add_option('--xml-no-stderr', dest='xml_capture_stderr', default=True,
            action="store_false",
            help="Disable capturing of stderr output." \
                    " This is especially useful when things are dieing without" \
                    " displaying an exception traceback.")

    def configure(self,options,conf):
        self.enabled = options.xml_enabled
        self.capture_stderr = options.xml_capture_stderr
        if not self.enabled or not options.xml_formatter:
            self.enabled = False
            self.formatter = None
        else:
            ( modName, clsName ) = options.xml_formatter.rsplit( '.', 1 )
            __import__(modName)
            self.cls_inst = getattr( sys.modules[modName], clsName )
            self.formatter = self.cls_inst( self.sys.stdout )

    def setOutputStream(self,stream):
        self.old_stream = stream
        return self.redirect

    def prepareTestResult(self,result):
        #Monkey patch the TextTestResult to not print
        #it's summary.
        result.dots = False
        def _mpPrintSummary(start,stop):
            pass
        result.printSummary = _mpPrintSummary

    def begin(self):
        self._start()
        self.formatter.startDocument()

    def finalize(self,result):
        self.formatter.startElement( 'reports', attrs={} )
        self.formatter.characters( self._escape( self.redirect.buf.getvalue() ) )
        self.formatter.endElement( 'reports' )
        self._writeCaptured()
        self.formatter.startElement( 'results', attrs={ 'ran': self.ran, 'errors': self.errors, 'failures': self.failures } )
        self.formatter.endElement( 'results' )
        self.formatter.endDocument()
        while self.stdout:
            self._end()
        linecache.clearcache()

    def beforeTest(self,test):
        self.ran += 1
        self._start()

    def afterTest(self,test):
        self._end()

    def addSuccess(self,test):
        self.formatter.startElement( 'test', { 'id': self._id( test ), 'status': 'success' } )
        self._writeCaptured()
        self.formatter.endElement( 'test' )

    def handleError(self,test,err):
        self.errors += 1
        self.formatter.startElement( 'test', { 'id': self._id( test ), 'status': 'error' } )
        self._writeTraceback( err )
        self._writeCaptured()
        self.formatter.endElement( 'test' )
        return True
        
    def handleFailure(self,test,err):
        self.failures += 1
        self.formatter.startElement( 'test', { 'id': self._id( test ), 'status': 'failure' } )
        self._writeTraceback( err )
        self._writeCaptured()
        self.formatter.endElement('test')
        return True

    def _start(self):
        self.stdout.append(self.sys.stdout)
        self.outbuf = self.sys.stdout = self.stringio()
        if self.capture_stderr:
            self.stderr.append(self.sys.stderr)
            self.errbuf = self.sys.stderr = self.stringio()

    def _end(self):
        if self.stdout:
            self.sys.stdout = self.stdout.pop()
        if self.stderr:
            self.sys.stderr = self.stderr.pop()

    def _writeCaptured(self):
        if self.outbuf and self.outbuf.getvalue().strip():
            self.formatter.startElement('stdout', attrs={})
            self.formatter.characters(self._escape(self.outbuf.getvalue()))
            self.formatter.endElement('stdout')
            self.outbuf = None
        if self.capture_stderr and self.errbuf and self.errbuf.getvalue().strip():
            self.formatter.startElement('stderr', attrs={})
            self.formatter.characters(self._escape(self.errbuf.getvalue()))
            self.formatter.endElement('stderr')
            self.errbuf = None

    def _writeTraceback(self,exc_info):
        import traceback
        self.formatter.startElement('traceback', attrs={})

        tb = exc_info[2]
        while tb:
            frame = tb.tb_frame
            line = tb.tb_lineno
            tb = tb.tb_next
            fname = frame.f_code.co_filename
            func = frame.f_code.co_name
            if '__unittest' in frame.f_globals:
                # this is the magical flag that prevents unittest internal
                # code from junking up the stacktrace
                continue
            linecache.checkcache(fname)
            text = linecache.getline(fname, line, frame.f_globals).strip()

            fname = self._escape( fname )
            line = self._escape( line )
            func = self._escape( func )
            text = self._escape( text )
            self.formatter.startElement( 'frame', { 'file': fname, 'line': line, 'function': func, 'text': text } )
            self.formatter.endElement( 'frame' )
        etype = ''.join( [ f.strip() for f in traceback.format_exception_only( exc_info[0], '' ) ] )
        etype = self._escape( etype )
        cause = self._escape( exc_info[1] )
        self.formatter.startElement('cause', { 'type': etype } )
        self.formatter.characters( cause )
        self.formatter.endElement( 'cause' )
        self.formatter.endElement('traceback')

    def _id(self,test):
        try:
            return self._escape( test.id() )
        except:
            pass
        if isinstance( test, nose.suite.ContextSuite ):
            return self._escape( 'nose.suite.ContextSuite(%s)' % test.context or 'Unknown' )
        log.warning( "Uknown class: %s.%s" % ( test.__class__.__module__, test.__class__.__name__ ) )
        return self._escape( test )
        
    def _escape(self,data):
        ret = str( data )
        for e in self.escapes:
            ret = e[0].sub( e[1], ret )
        return ret
