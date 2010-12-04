import os
import sys
import logging
import pickle

log = logging.getLogger(__name__)
debug = log.debug

from shared import const
from shared.state import FileSystemState, FileSystemStateManager

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
				ret.check()
				loaded = True
				debug("loaded: %s" % (picklefile.name,))
			except StandardError, e:
				errmsg = "Failed loading \"%s\". (Error was %s: \"%s\")" % (const.picklefile_name, type(e).__name__, e.message)
				log.error(errmsg, exc_info=1)
				print >> sys.stderr, errmsg
				picklefile.close()
				if tried_deleting:
					sys.exit(1)
				print >> sys.stderr, "Deleting picklefile and trying again..."
				tried_deleting = True
				reset()
	except IOError:
		debug("IOError:", exc_info=sys.exc_info())
		ret = FileSystemState()
	manager = FileSystemStateManager(ret)
	manager.update()
	return manager

def save(state):
	picklefile = open_file(pickle_path(), 'w')
	assert isinstance(state, FileSystemState)
	pickle.dump(state, picklefile)
	picklefile.close()
	debug("saved dependencies file: %s" % (picklefile.name))

def reset():
	path = pickle_path()
	if os.path.isfile(path):
		os.remove(path)
