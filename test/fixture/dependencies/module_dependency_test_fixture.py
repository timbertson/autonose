from unittest import TestCase

class ModuleTestDependencyFixture(TestCase):
	def test_module_imports(self):
		from includeddir import thingObject
