from unittest import TestCase
import types

from sniffles.watcher.module_tools import *
from ..test_helper import sniffles_root

def last_two_file_components(path):
	return '/'.join(path.split(os.path.sep)[-2:])

def in_sniffles(path):
	return path.startswith(sniffles_root)

class ModuleToolsTest(TestCase):
	def test_should_detect_module_files(self):
		watcher = __import__('sniffles.watcher')
		files = all_module_files(watcher)
		cwd_mask = filter(in_sniffles, files)
		bases = map(last_two_file_components, cwd_mask)
		expected_files = [
			'sniffles/__init__.pyc',
			'watcher/__init__.pyc',
			'watcher/watcher.pyc']
		self.assertTrue(set(expected_files).issubset(set(bases)), bases)
	
	def test_should_filter_only_parent_module_files(self):
		watcher = __import__('sniffles.watcher.watcher')
		files = all_parent_module_files('sniffles.watcher.watcher', watcher)
		bases = map(last_two_file_components, files)
		self.assertEqual(
			sorted([
				'sniffles/__init__.pyc',
				'watcher/__init__.pyc',
				'watcher/watcher.pyc']),
			sorted(bases))
	
	def test_should_create_a_list_of_valid_parent_files_from_a_module_name(self):
		self.assertEqual(sorted(valid_parent_file_base_paths('x.y.z')),
			sorted(['x/__init__','x/y/__init__', 'x/y/z/__init__','x/y/z']))
	
	def test_should_find_the_canonical_module_file(self):
		file_ = canonical_module_file(
			'sniffles.watcher.watcher',
			[	'path/to/sniffles/__init__.pyc',
				'path/to/sniffles/watcher/__init__.pyc',
				'path/to/sniffles/watcher/watcher.pyc'])
		self.assertEqual(file_, 'path/to/sniffles/watcher/watcher.pyc')
	
	def test_should_fallback_to_a___init___file_if_one_exists(self):
		file_ = canonical_module_file(
			'sniffles.watcher',
			[	'path/to/sniffles/__init__.pyc',
				'path/to/sniffles/watcher/__init__.pyc'])
		self.assertEqual(file_, 'path/to/sniffles/watcher/__init__.pyc')

