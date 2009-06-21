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

def load():
	path = pickle_path()
	ret = None
	try:
		picklefile = open(path)
		try:
			ret = pickle.load(picklefile)
		except StandardError, e:
			errmsg = "Failed loading \"%s\". you may have to delete it (Error was %s: \"%s\")" % (const.picklefile_name, type(e).__name__, e.message)
			log.error(errmsg, exc_info=1)
			print >> sys.stderr, errmsg
			sys.exit(1)
		finally:
			picklefile.close()
		debug("loaded: %s" % (picklefile.name,))
	except IOError:
		debug("IOError:", exc_info=sys.exc_info())
		ret = {}
	return ret

def save(state_ = None):
	if state_ is None:
		state_ = state
	picklefile = open(pickle_path(), 'w')
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
