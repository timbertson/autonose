from unittest import TestCase
import types

from sniffles.watcher.import_monitor import ImportMonitor
from ..test_helper import sniffles_root

class ImportMonitorTest(TestCase):
	def setUp(self):
		self.importer = ImportMonitor(sniffles_root)
	
	def tearDown(self):
		self.importer.end()
		self.importer = None

	def test_should_monitor_imports(self):
		from dummy_module import thing
		imported_files = self.importer.imported
		file_paths = map(lambda x: x.path, imported_files)
		self.assertEqual(['test/watcher/dummy_module.py'], file_paths)
		self.importer.reset()
		self.assertEqual(self.importer.imported, [])
	
	def test_should_return_canonical_name_for_an_import(self):
		self.assertEqual(self.importer.path_for_module('test.test_helper'), 'test/test_helper.py')
		self.assertTrue('test/__init__.py' in self.importer.imported)
	
	def test_should_not_capture_imports_after_end(self):
		self.importer.reset()
		self.importer.end()
		import dummy_module
		self.assertEqual(self.importer.imported, [])
		
		self.importer._insert_import() # so tearDown won't fail


