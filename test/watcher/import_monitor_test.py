from unittest import TestCase
import types

from sniffles.watcher.import_monitor import ImportMonitor
from ..test_helper import sniffles_root

class ImportMonitorTest(TestCase):
	def setUp(self):
		self.importer = ImportMonitor(sniffles_root)
		self.importer.start()
	
	def tearDown(self):
		self.importer.stop()
		self.importer = None

	def test_should_monitor_imports(self):
		from ..fixture.dependencies.includeddir import thing
		imported_files = self.importer.imported
		file_paths = map(lambda x: x.path, imported_files)
		self.assertTrue('test/fixture/dependencies/includeddir/thing.py' in file_paths, file_paths)
		self.importer.reset()
		self.assertEqual(self.importer.imported, [])
	
	def test_should_return_canonical_name_for_an_import(self):
		self.assertEqual(self.importer.path_for_module('test.test_helper'), 'test/test_helper.py')
		self.assertTrue('test/__init__.py' in self.importer.imported)
	
	def test_should_not_capture_imports_after_end(self):
		self.importer.reset()
		self.importer.stop()
		from ..fixture.dependencies.includeddir import thing
		self.assertEqual(self.importer.imported, [])
		


