import os
from const import cwd

class FileOutsideCurrentRoot(RuntimeError):
	pass

_default = object()
def relative(path, default=_default):
	realpath = os.path.realpath(path)
	if realpath.startswith(cwd):
		return realpath[len(cwd)+1:]
	if default is not _default:
		return default
	raise FileOutsideCurrentRoot(realpath)

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


