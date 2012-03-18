from mocktest import *
from autonose.ui.shared.page import Page, Summary

class SummaryTest(TestCase):
	def setUp(self):
		self.summary = Summary()

	def test_success_formatting(self):
		self.summary.ran += 5
		self.assertMatches(string_containing(
			'ran <span class="tests">5 tests</span>'
		), str(self.summary))
		assert 'failures' not in str(self.summary)
		assert 'errors' not in str(self.summary)

	def test_fail_formatting(self):
		self.summary.ran += 5
		self.assertMatches(string_containing(
			'ran <span class="tests">5 tests</span>'
		), str(self.summary))
		assert 'failures' not in str(self.summary)
		assert 'errors' not in str(self.summary)
	
	def test_error_formatting(self):
		self.summary.ran += 5
		self.summary.errors += 1
		self.assertMatches(string_containing(
			'ran <span class="tests">5 tests</span> '
			'(<span class="errors">1 errors</span>)'
		), str(self.summary))
		assert 'failures' not in str(self.summary)

	def test_combination_formatting(self):
		self.summary.ran += 5
		self.summary.failures += 2
		self.summary.errors += 2
		self.assertMatches(string_containing(
			'ran <span class="tests">5 tests</span> '
			'(<span class="failures">2 failures</span>, '
			'<span class="errors">2 errors</span>)'
		), str(self.summary))
