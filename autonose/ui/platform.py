import sys

def default_app():
	platform = sys.platform
	App = None
	if platform.startswith('linux'):
		from gtkapp import App
	else:
		raise RuntimeError("Unknown platform name: %r" % (platform,))
	return App
