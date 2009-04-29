from mocktest import *

from sniffles.shared.test_result import TestResult, TestResultSet

class TestResultTest(TestCase):
	def test_should_store_state__name__time__and_err(self):
		state, test, err, time = 'success', mock('test'), mock('error'), mock('time')
		tr = TestResult(state, test, err, time)
		self.assertEqual(tr.state, state)
		self.assertEqual(tr.name, str(test))
		self.assertEqual(tr.err, err)
		self.assertEqual(tr.time, time)
	
	def test_should_validate_state(self):
		self.assertRaises(ValueError, lambda: TestResult('notastate', None, None, None))

	def test_should_be_ok_if_state_is_in_acceptable_states(self):
		self.assertTrue(TestResult('success', None, None, None).ok())
		self.assertTrue(TestResult('skipped', None, None, None).ok())
	
	def test_should_not_be_ok_if_state_is_not_in_acceptable_states(self):
		self.assertFalse(TestResult('fail', None, None, None).ok())
		self.assertFalse(TestResult('error', None, None, None).ok())
	
class TestResultSetTest(TestCase):
	def result_mock(self, **kwargs):
		opts = dict(time=0, ok=False)
		opts.update(kwargs)
		return mock().with_methods(**kwargs).unfrozen()
		
	def test_should_not_be_ok_if_any_result_is_not(self):
		ok1 = self.result_mock(ok = True).named('ok1')
		ok2 = self.result_mock(ok = True).named('ok2')
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
	
	def test_should_clear_all_non_newest_result_on_add(self):
		old = self.result_mock(time=1).named('old')
		new = self.result_mock(time=2).named('new')
		new2 = self.result_mock(time=2).named('new2')
		trs = TestResultSet()
		trs.add(old.raw)
		self.assertEqual(trs.results, [old.raw])
		trs.add(new.raw)
		self.assertEqual(trs.results, [new.raw])
		trs.add(new2.raw)
		self.assertEqual(trs.results, [new.raw, new2.raw])
		
