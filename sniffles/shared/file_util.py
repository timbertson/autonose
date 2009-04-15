import os
from const import cwd

def relative(path):
	realpath = os.path.realpath(path)
	if realpath.startswith(cwd):
		return realpath[len(cwd)+1:]
	return None

def absolute(path):
	if os.path.isabs(path):
		return path
	return os.path.join(cwd, path)

def is_pyfile(path):
	return '.' in path and (path.rsplit('.',1)[-1].lower() == 'py')


