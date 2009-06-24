"""
Copyright (c) 2008 Paul Davis <paul.joseph.davis@gmail.com>

This file is part of nosexml, which is released under the MIT license.
"""

class XMLFormatter(object):
    """Base XMLFormatter class

        For those wanting to design their own XML output format, this is
        the class that should be inherited and passed to nosetests in the
        --xml-formatter command line argument.
        
        All in all its fairly simple. You should mostly think of it as a
        reverse SAX parser. 
    """
    def __init__(self,stream):
        self.stream = stream
    def setStream(self,stream):
        raise NotImplementedError()
    def startDocument(self):
        """
        This is called when once at the beginning of a run. Generally it
        is responsible for writing the doctype declaration and opnening
        element of the XML document.
        """
        raise NotImplementedError()
    def endDocument(self):
        """
        Called once when a unittest run has completed. Generally this is
        responsible for writing the closing document element.
        """
        raise NotImplementedError()
    def startElement(self,name,attrs={}):
        """
        Called when new elements are available for consumption. A brief
        list of elements to be concerned about:
        
          # Element Name - Attribute List
          # test - id, status
          # traceback
          # frame - file, line, function, text
          # cause - type
          # stdout
          # stderr
          # reports
          # results - ran, errors, failures
        """
        raise NotImplementedError()
    def endElement(self,name):
        """
        Called to end a element balanced with the calls to startElement
        """
        raise NotImplementedError()
    def characters(self,data):
        """
        Any chacter data associated with the tag. The content is XML
        escaped before being passed to this method.
        """
        raise NotImplementedError()
