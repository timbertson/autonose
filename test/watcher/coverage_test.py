from unittest import TestCase
from commands import getstatusoutput
from os import path
import pickle

from sniffles.watcher.watcher import picklefile_name

class TestCoverage(TestCase):
	def test_fixture_should_depend_on_all_included_files(self):
		fixture_path = path.join(path.dirname(__file__), '..','fixture','coverage')
		st, out = getstatusoutput(
			"cd '%s' && nosetests --with-sniffles --debug=sniffles" %
				(fixture_path))
		if st != 0:
			raise OSError(out)
		picklefile = open(path.join(fixture_path, picklefile_name))
		depends = pickle.load(picklefile)
		picklefile.close()
		
		self.assertEqual(depends.keys(), ['coverage_test_fixture'])
		depended_filestamps = depends['coverage_test_fixture']
		depended_files = map(lambda x: x.path, depended_filestamps)
		self.assertEqual(sorted(depended_files), ['coverage_test_fixture.py', 'included1.py', 'included2.py'])

