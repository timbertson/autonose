import os
from const import cwd

def relative(path):
	realpath = os.path.realpath(path)
	if realpath.startswith(cwd):
		return realpath[len(cwd)+1:]
	return None

def source(path):
	return path[:-1] if ext(path) == 'pyc' else path

def absolute(path):
	if os.path.isabs(path):
		return path
	return os.path.join(cwd, path)

def ext(path):
	return path.rsplit('.',1)[-1].lower()

def is_pyfile(path):
	return '.' in path and ext(path) == 'py'


