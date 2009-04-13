from unittest import TestCase

class TestDependencyFixture(TestCase):
	def test_1(self):
		import included1 as incl
	
	def test_multi(self):
		import included1, included2 as incl2
		import os
		import sys
	
	def test_2(self):
		import included2

