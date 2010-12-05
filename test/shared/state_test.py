from .. import test_helper

from mocktest import *

#TODO: fill in all these tests!

class StateTest(TestCase):
	def test_anything_changed_should_be_affected_by_changed__added_and_removed_files(self):
		pass
	
	def test_update_should_ignore_dot_files(self):
		pass
	
	def test_update_should_inspect_all_files_using_relative_paths(self):
		pass
	
	def test_inspect_should_skip_already_seen_files(self):
		pass
	
	def test_inspect_should_track_removed_files(self):
		pass
	
	def test_inspect_should_track_added_files(self):
		pass
	
	def test_inspect_should_track_changed_files(self):
		pass

	def test_inspect_should_ignore_unchanged_files(self):
		pass
	
	def test_affected_should_be_the_transitive_dependencies_of_added_removed_and_updated_files(self):
		pass
		
	def test_bad_should_be_all_affected_and_non__ok_files(self):
		pass
	
	def test_file_state_should_be_indexable_by_relative_file_path(self):
		#TODO: this is probably a poor idea...
		pass
	
	def test_should_return_modified_files_without_propagating_changes(self):
		pass

