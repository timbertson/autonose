import urllib
import cgi

file_protocol = 'file://'
def editable_file(url):
	return url.startswith(file_protocol) and urllib.splitquery(url)[0].endswith('.py')
	
def path_and_line_from(url):
	if not url.startswith(file_protocol):
		raise ValueError("URI (%s) is not a '%s' URI" % (url, file_protocol))
	url = url[len(file_protocol):]
	path, query = urllib.splitquery(url)
	path = urllib.url2pathname(path)
	line = 0
	try:
		if query:
			query_dict = cgi.parse_qs(query)
			line = query_dict['line'][0]
	except (IndexError, KeyError): pass
	return (path, line)

