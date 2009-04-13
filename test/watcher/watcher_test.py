from unittest import TestCase
from commands import getstatusoutput
from os import path
import pickle

from sniffles.shared.const import picklefile_name
from sniffles import watcher

from .. import test_helper

class TestDependencyDiscovery(TestCase):
	def run_fixture(self, fixture_path, *modules):
		module_arg = ' '.join(modules)
		cmd = "cd '%s' && nosetests --with-sniffles --debug=sniffles %s" % (fixture_path, module_arg)
		print cmd
		st, out = getstatusoutput(cmd)
		if st != 0:
			raise OSError("command `%s` failed:\n%s" %(cmd, out))
		print out
		return out
	
	def path(self, relpath):
		return path.join(path.dirname(__file__), *relpath.split('/'))
	
	def test_fixture_should_depend_on_all_included_files(self):
		fixture_path = self.path('../fixture')
		output = self.run_fixture(fixture_path, 'dependencies.dependency_test_fixture')
		depends = watcher.load_dependencies(fixture_path)
		print depends
		
		self.assertEqual(depends.keys(), ['dependencies/dependency_test_fixture.py'])
		depended_filestamps = depends['dependencies/dependency_test_fixture.py']
		depended_files = map(lambda x: x.path, depended_filestamps)
		self.assertEqual(sorted(depended_files), ['dependencies/__init__.py', 'dependencies/dependency_test_fixture.py', 'dependencies/included1.py', 'dependencies/included2.py'])

