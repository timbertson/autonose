from mocktest import *

from autonose.shared.test_result import TestResult, TestResultSet

class TestResultTest(TestCase):
	def test_should_store_state(self):
		state = 'success'
		self.assertEqual(TestResult(state, None, None, None).state, state)
		
	def test_should_store_name_from_test(self):
		test = mock('test').with_methods(__str__ = 'test_str')
		self.assertEqual(TestResult('success', test.raw, None, None).name, 'test_str')
		
	def test_should_store_time(self):
		time = stub('time')
		self.assertEqual(TestResult('success', None, None, time).time, time)

	def test_should_store_err(self):
		err = mock('error').with_methods(__str__ = 'err')
		self.assertEqual(TestResult('success', None, err.raw, None).err, 'err')

	def test_should_not_convert_error_to_string_when_it_is_none(self):
		err = None
		self.assertTrue(TestResult('success', None, err, None).err is None)
	
	def test_should_validate_state(self):
		self.assertRaises(ValueError, lambda: TestResult('notastate', None, None, None))

	def test_should_be_ok_if_state_is_in_acceptable_states(self):
		self.assertTrue(TestResult('success', None, None, None).ok())
		self.assertTrue(TestResult('skipped', None, None, None).ok())
	
	def test_should_not_be_ok_if_state_is_not_in_acceptable_states(self):
		self.assertFalse(TestResult('fail', None, None, None).ok())
		self.assertFalse(TestResult('error', None, None, None).ok())
	
class TestResultSetTest(TestCase):
	def result_mock(self, name=None, time=0, ok=False):
		_mock = mock(name).with_children(time=time).unfrozen().with_methods(ok=ok)
		return _mock
		
	def test_should_not_be_ok_if_any_result_is_not(self):
		ok1 = self.result_mock(ok = True, name='ok1')
		ok2 = self.result_mock(ok = True, name='ok2')
		not_ok = self.result_mock(ok = False)
		trs = TestResultSet()
		trs.add(ok1.raw)
		trs.add(ok2.raw)
		trs.add(not_ok.raw)
		self.assertFalse(trs.ok())
		
	def test_should_be_ok_if_all_results_are(self):
		ok1 = self.result_mock(ok = True)
		ok2 = self.result_mock(ok = True)
		trs = TestResultSet()
		trs.add(ok1.raw)
		trs.add(ok2.raw)
		self.assertTrue(trs.ok())
	
	def test_should_be_ok_with_no_test_cases(self):
		trs = TestResultSet()
		self.assertTrue(trs.ok())
		
	def test_should_clear_all_non_newest_results_on_add(self):
		old = self.result_mock(time=1, name='old')
		new = self.result_mock(time=2, name='new')
		new2 = self.result_mock(time=2, name='new2')
		trs = TestResultSet()
		
		trs.add(old.raw)
		self.assertEqual(trs.results, [old.raw])
		trs.add(new.raw)
		self.assertEqual(trs.results, [new.raw])
		trs.add(new2.raw)
		self.assertEqual(trs.results, [new.raw, new2.raw])
		
