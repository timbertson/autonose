"""
Copyright (c) 2008 Paul Davis <paul.joseph.davis@gmail.com>

This file is part of nosexml, which is released under the MIT license.
"""

import sys
import urllib
from formatter import XMLFormatter

class TextMateFormatter(XMLFormatter):
    def __init__(self,stream):
        self.stream = stream
        self.state = []

    def setStream(self,stream):
        self.stream = stream

    def startDocument(self):
        self.stream.write(HTML_HEADER)
        self.stream.flush()
        
    def endDocument(self):
        self.stream.write(HTML_FOOTER)
        self.stream.flush()

    def startElement(self, name, attrs):
        getattr(self, "start_%s" % name)(attrs)
        self.stream.flush()

    def endElement(self,name):
        getattr(self, "end_%s" % name)()
        self.stream.flush()

    def characters(self,data):
        self.stream.write(data.strip())
        self.stream.flush()

    def start_test(self, attrs):
        html = """
            <li class="%(status)s">
                <a href="javascript:toggle( '%(id)s', 'show' )" id="%(id)s_s">&#x25B6;</a>
                <a href="javascript:toggle( '%(id)s', 'hide' )" id="%(id)s_h" style="display: none;">&#x25BC;</a>
                <h2>%(id)s</h2>
                <div id="%(id)s" class="content">
        """
        self.stream.write(html % attrs)
    
    def end_test(self):
        html = """
                </div>
                <script type="text/javascript">
                    scroll_to_bottom() ;
                </script>
            </li>
        """
        self.stream.write(html)

    def start_traceback(self, attrs):
        html = """<ul class="traceback">\n"""
        self.stream.write(html)

    def end_traceback(self):
        html = "</ul>\n"
        self.stream.write(html)

    def start_frame(self, attrs):
        attrs['url'] = 'file://%s' % urllib.quote(attrs['file'])
        html = """
            <li>
                <tt><a href="txmt://open?url=%(url)s&line=%(line)s">%(file)s(%(line)s): %(function)s</a></tt>
                <pre>    %(text)s</pre>
            </li>
        """
        self.stream.write(html % attrs)

    def end_frame(self):
        pass

    def start_cause(self, attrs):
        self.stream.write("<li><pre>%(type)s: ")

    def end_cause(self):
        self.stream.write("</pre></li>\n")

    def start_stdout(self, attrs):
        self.stream.write("<pre>\n")
    
    def end_stdout(self):
        self.stream.write("\n</pre>\n")

    def start_stderr(self, attrs):
        self.stream.write("<pre>\n")
    
    def end_stderr(self):
        self.stream.write("\n</pre>\n")

    def start_reports(self, attrs):
        html = """
            <li>
                <a href="javascript:toggle( 'reports', 'show' )" id="reports_s">&#x25B6;</a>
                <a href="javascript:toggle( 'reports', 'hide' )" id="reports_h" style="display: none;">&#x25BC;</a>
                <h2>Reports</h2>
                <div id="reports" class="content" style="display: none;"><pre>"""
        self.stream.write(html)
    
    def end_reports(self):
        self.stream.write("</pre></div></li>\n")

    def start_results(self, attrs):
        html = """
            <li>
                <em>Ran</em> %(ran)s
                <em>Errors</em> %(errors)s
                <em>Failures</em> %(failures)s
            </li>
        """
        self.stream.write(html % attrs)

    def end_results(self):
        pass

HTML_HEADER = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html>
    <head>
        <title>Nosetests Error Report</title>
        <style type="text/css">
            body
            {
                font-family: Lucida Grande ;
            }

            a
            {
                color: blue ;
                text-decoration: none ;
            }

            ul
            {
                padding: 0px ;
                margin: 0px ;
                list-style-type: none ;
            }

            ul li
            {
                padding: 5px ;
                margin: 0px ;
                margin-bottom: 5px ;
                border: 1px solid #CCCCCC ;
            }

            h2
            {
                display: inline ;
                margin: 0px ;
                padding: 0px ;
                font-size : 14px ;
            }

            ul li.success h2
            {
                color: green ;
            }

            ul li.success .content
            {
                display: none ;
            }

            ul li.error h2
            {
                color: orange ;
            }

            ul li.failure h2
            {
                color: red ;
            }

            ul.traceback li
            {
                border: none ;
                padding: 0px ;
                margin: 0px ;
            }

            ul.traceback li pre
            {
                padding: 0px ;
                margin: 0px ;
            }

            div.content
            {
                margin: 10px ;
                margin-left: 25px ;
                font-size: 12px ;
            }
        </style>
        <script type="text/javascript">
            function scroll_to_bottom()
            {
                var height = document.documentElement.clientHeight ;
                window.scrollTo( 0, height ) ;
            }

            function toggle( id, action )
            {
                var d = document.getElementById( id ) ;
                var s = document.getElementById( id + "_s" ) ;
                var h = document.getElementById( id + "_h" ) ;

                if( action == 'hide' )
                {
                    d.style.display = "none" ;
                    s.style.display = "inline" ;
                    h.style.display = "none" ;
                }
                else if( action == "show" )
                {
                    d.style.display = "block" ;
                    s.style.display = "none" ;
                    h.style.display = "inline" ;
                }
            }
        </script>
    </head>
    <body>
        <ul>
"""

HTML_FOOTER = """
        </ul>
        <script type="text/javascript">
            scroll_to_bottom() ;
        </script>
    </body>
</html>
"""
