
class SomeError(Exception):
	pass

def foo():
	raise SomeError()

def test_foo():
	foo()
