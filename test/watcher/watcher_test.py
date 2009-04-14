from unittest import TestCase
from commands import getstatusoutput
import os
from os import path
import pickle

from sniffles.shared.const import picklefile_name
from sniffles import watcher
from sniffles.shared import const

from .. import test_helper

def difference(a, b):
	return a.difference(b).union(b.difference(a))

class TestDependencyDiscovery(TestCase):
	
	def assertSetEqual(self, a, b):
		sa = set(a)
		sb = set(b)
		self.assertEqual(sa, sb, "\n   %r != \n   %r\n\nDiffering items:   %r" % (sorted(a), sorted(b), sorted(difference(sa, sb))))
		
	def run_fixture(self, fixture_path, *modules):
		module_arg = ' '.join(modules)
		try:
			os.remove(path.join(fixture_path, const.picklefile_name))
		except OSError, e:
			print "deleting previous picklefile didn't work: %s - it's okay if it doesn't exist" % (e.message)
		cmd = "cd '%s' && nosetests --with-sniffles --debug=sniffles %s" % (fixture_path, module_arg)
		print cmd
		st, out = getstatusoutput(cmd)
		if st != 0:
			raise OSError("command `%s` failed:\n%s" %(cmd, out))
		print out
		return out
	
	def path(self, relpath):
		return path.join(path.dirname(__file__), *relpath.split('/'))
	
	def test_fixture_should_depend_on_all_included_files_and_modules(self):
		fixture_path = self.path('../fixture')
		output = self.run_fixture(fixture_path, 'dependencies')
		depends = watcher.load_dependencies(fixture_path)
		print depends

		dependency_tree_paths_only = {}
		for key, dependency_list in depends.items():
			dependency_tree_paths_only[key] = map(lambda x: x.path, dependency_list)
		
		expected_dependencies = {
			'dependencies/dependency_test_fixture.py': [
				'__init__.py',
				'dependencies/__init__.py',
				'dependencies/dependency_test_fixture.py',
				'dependencies/included1.py',
				'dependencies/included2.py',
				'dependencies/included3.py'],

			'dependencies/module_dependency_test_fixture.py': [
				'__init__.py',
				'dependencies/__init__.py',
				'dependencies/module_dependency_test_fixture.py',
				'dependencies/includeddir/__init__.py',
				'dependencies/includeddir/thing.py'],

			'dependencies/includeddir/__init__.py': [
				'dependencies/includeddir/thing.py'],

			'dependencies/__init__.py': [],
		}
		
		self.assertSetEqual(depends.keys(), expected_dependencies)
		for key, expected_dependency_list in expected_dependencies.items():
			self.assertSetEqual(dependency_tree_paths_only[key], expected_dependency_list)
			
