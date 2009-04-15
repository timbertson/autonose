import os
import logging

from shared.const import cwd
from snakefood import util, find
from snakefood.fallback.collections import defaultdict

logging.basicConfig(level=logging.DEBUG)

log = logging.getLogger(__name__)
debug = log.debug
info = log.info

def filename(abspath):
	#TODO: return relpath; or None to ignore this file
	realpath = os.path.realpath(abspath)
	if realpath.startswith(cwd):
		return realpath[len(cwd)+1:]
	return None

def add(dict_, key, dep=None):
	if key not in dict_:
		dict_[key] = set()
	if dep is not None:
		dict_[key].add(dep)

def gen(*paths):
	fiter = util.iter_pyfiles(paths, ignores=None, abspaths=True)
	allerrors = []
	allfiles = {}
	while 1:
		newfiles = set()
		for fn in fiter:
			if fn in allfiles:
				continue # Make sure we process each file only once.

			info("	%s" % fn)

			if util.is_python(fn):
				files, errors = find.find_dependencies(fn, verbose=False, process_pragmas=False)
				allerrors.extend(errors)
			else:
				files = []

			# Make sure all the files at least appear in the output, even if it has
			# no dependency.
			from_ = filename(fn)
			if from_ is None:
				continue
			add(allfiles, from_)

			# Add the dependencies.
			for child in files:
				debug(child)
				to_ = filename(child)
				if to_ is None:
					continue
				add(allfiles, from_, to_)
				newfiles.add(child)

		if not newfiles:
			break
		else:
			fiter = iter(newfiles)
	print repr(allfiles)
	return allfiles

if __name__ == '__main__':
	gen(cwd)

