import sys

def default_app():
	platform = sys.platform
	app = None
	if platform.startswith('linux'):
		from gtkapp import App
	elif platform == 'darwin':
		from cocoa import App
	else:
		raise RuntimeError("Unknown platform name: %r" % (platform,))
	return App
