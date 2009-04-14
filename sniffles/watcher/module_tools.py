import os
import types

def file_base(path):
	return remove_extension(os.path.basename(path))

def remove_extension(path):
	return path.rsplit('.', 1)[0]

def _accumulate_all_module_files(accumulator_set, module_object):
	"""
	for the given module and all sub-modules, add each module.__file__
	path to accumulator_set.
	"""
	try:
		file_ = module_object.__file__
	except AttributeError:
		# debug("module %s has no __file__ attribute" % (module_object,))
		return
	if file_ in accumulator_set:
		return

	accumulator_set.add(file_)
	if os.path.basename(file_).startswith('__init__.'):
		for key, value in module_object.__dict__.items():
			if not isinstance(value, types.ModuleType):
				# debug("module.%s is not of type module" % (key,))
				continue
			_accumulate_all_module_files(accumulator_set, value)

def all_module_files(module_object):
	files = set()
	_accumulate_all_module_files(files, module_object)
	return files

def all_parent_module_files(module_name, module_object):
	module_files = all_module_files(module_object)
	possible_paths = valid_parent_file_base_paths(module_name)
	parent_files = []
	
	for file_ in module_files:
		file_base = remove_extension(file_)
		for module_path in possible_paths:
			if file_base.endswith(module_path):
				parent_files.append(file_)
	return parent_files

def valid_parent_file_base_paths(module_name):
	"""
	return all possible parent path endings (minus extensions) for the given module name.
	e.g: given "some.test.module", possible parent file paths are:
	     - some/__init__
	     - some/test/__init__
	     - some/test/module
	     - some/test/module/__init__
	"""
	module_parts = module_name.split('.')
	path_endings = []
	previous_parts = []
	path_endings.append(os.path.join(*module_parts))
	for part in module_parts:
		previous_parts.append(part)
		path_endings.append(os.path.join(*(previous_parts + ['__init__'])))
	return path_endings

def canonical_module_file(module_name, module_file_set):
	"""
	given a module name and file set, return the '.py' file the looks
	the most like it is the actual source file for that module
	"""
	module_path = os.path.join(*str(module_name).split('.'))
	def file_matching_module_path(path):
		for file_ in module_file_set:
			if remove_extension(file_).endswith(path):
				return file_
		return None
	file_ = file_matching_module_path(module_path)
	if file_ is None:
		file_ = file_matching_module_path(os.path.join(module_path, '__init__'))
	if file_ is not None:
		return file_
	raise ValueError("module %s does not seem to have a canonical .py file in its module tree: %s" % (module_name, module_file_set))

