from mocktest import *

from autonose.shared.test_result import TestResult, TestResultSet
def make_result(state, id=None, name=None, address=None, path=None, err=None, run_start=None, outputs=[]):
	return TestResult(state, id, name, address, path, err, run_start, outputs)


class TestResultTest(TestCase):
	def test_should_store_state(self):
		state = 'success'
		self.assertEqual(make_result(state).state, state)
		
	def test_should_store_name_from_test(self):
		self.assertEqual(make_result('success', name='test_str').name, 'test_str')
		
	def test_should_store_time(self):
		time = mock('time')
		self.assertEqual(make_result('success', run_start=time).time, time)

	def test_should_extract_trace_from_err(self):
		err = ('cls', 'instance', mock('traceback').with_child(tb_frame = []))
		self.assertEqual(make_result('success', err=err).outputs[0], ('traceback', ('cls', 'instance', [])))

	def test_should_validate_state(self):
		self.assertRaises(ValueError, lambda: make_result('notastate', None, None, None))

	def test_should_be_ok_if_state_is_in_acceptable_states(self):
		self.assertTrue(make_result('success', None, None, None).ok())
		self.assertTrue(make_result('skipped', None, None, None).ok())
	
	def test_should_not_be_ok_if_state_is_not_in_acceptable_states(self):
		self.assertFalse(make_result('fail', None, None, None).ok())
		self.assertFalse(make_result('error', None, None, None).ok())
	
class TestResultSetTest(TestCase):
	def result_mock(self, name=None, time=0, ok=False):
		_mock = mock(name).with_children(time=time).with_methods(ok=ok)
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
		
	def test_should_be_ok_if_all_results_are_success_or_skip(self):
		ok1 = make_result('success')
		ok2 = make_result('skipped')
		trs = TestResultSet()

		trs.add(ok1)
		trs.add(ok2)
		self.assertTrue(trs.ok())
	
	def test_should_be_ok_with_no_test_cases(self):
		trs = TestResultSet()
		self.assertTrue(trs.ok())
		
	def test_should_clear_all_non_newest_results_on_add(self):
		old = self.result_mock(time=1, name='old')
		new = self.result_mock(time=2, name='new')
		new2 = self.result_mock(time=2, name='new2')
		trs = TestResultSet()
		
		trs.add(old)
		self.assertEqual(trs.results, [old])
		trs.add(new)
		self.assertEqual(trs.results, [new])
		trs.add(new2)
		self.assertEqual(trs.results, [new, new2])
		
