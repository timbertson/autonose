import os
import sys
import logging
import pickle

log = logging.getLogger(__name__)
debug = log.debug

from shared import const
from shared.state import FileSystemState

state = None

def pickle_path():
	return os.path.join(const.cwd, const.picklefile_name)

def open_file(path, *a):
	return open(path, *a)

def load():
	path = pickle_path()
	ret = None
	loaded = False
	tried_deleting = False
	picklefile = None
	try:
		while not loaded:
			picklefile = open_file(path)
			try:
				ret = pickle.load(picklefile)
				loaded = True
			except StandardError, e:
				errmsg = "Failed loading \"%s\". (Error was %s: \"%s\")" % (const.picklefile_name, type(e).__name__, e.message)
				log.error(errmsg, exc_info=1)
				print >> sys.stderr, errmsg
				picklefile.close()
				if tried_deleting:
					sys.exit(1)
				tried_deleting = True
				os.remove(path)
			debug("loaded: %s" % (picklefile.name,))
	except IOError:
		debug("IOError:", exc_info=sys.exc_info())
		ret = {}
	return ret

def save(state_ = None):
	if state_ is None:
		state_ = state
	picklefile = open_file(pickle_path(), 'w')
	pickle.dump(state_.dependencies, picklefile)
	picklefile.close()
	debug("saved dependencies file: %s" % (picklefile.name))

def scan(dependencies = None):
	global state
	if state is None:
		if dependencies is None:
			dependencies = load()
		state = FileSystemState(dependencies)
	state.update()
	return state

def reset():
	path = pickle_path()
	if os.path.isfile(path):
		os.remove(path)
