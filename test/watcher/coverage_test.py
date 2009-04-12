from unittest import TestCase
from commands import getstatusoutput
from os import path
import pickle

from sniffles.watcher import picklefile_name

class TestCoverage(TestCase):
	def run_fixture(self, relpath, *modules):
		fixture_path = path.join(path.dirname(__file__), *relpath.split('/'))
		module_arg = ' '.join(modules)
		cmd = "cd '%s' && nosetests --with-sniffles --debug=sniffles %s" % (fixture_path, module_arg)
		print cmd
		st, out = getstatusoutput(cmd)
		if st != 0:
			raise OSError("command `%s` failed:\n%s" %(cmd, out))
		return out
	
	def pickle_file(self, relpath):
		base = path.join(path.dirname(__file__), *relpath.split('/'))
		picklefile = open(path.join(base, picklefile_name))
		depends = pickle.load(picklefile)
		picklefile.close()
		return depends
		
	def test_fixture_should_depend_on_all_included_files(self):
		fixture_path = '../fixture'
		output = self.run_fixture(fixture_path, 'coverage.coverage_test_fixture')
		depends = self.pickle_file(fixture_path)
		
		self.assertEqual(depends.keys(), ['coverage.coverage_test_fixture'])
		depended_filestamps = depends['coverage.coverage_test_fixture']
		depended_files = map(lambda x: x.path, depended_filestamps)
		self.assertEqual(sorted(depended_files), ['coverage/__init__.py', 'coverage/coverage_test_fixture.py', 'coverage/included1.py', 'coverage/included2.py'])

