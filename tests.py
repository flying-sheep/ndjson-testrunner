import re
import json
import unittest
from collections import namedtuple
from io import StringIO
from typing import Optional, Union, re as re_t

from ndjson_testrunner import JSONTestRunner


StructuredResult = namedtuple('StructuredResult', 'type id desc msg')


class TestsToBeTested(unittest.TestCase):
	"""Those tests are not there to pass, but to create all kinds of output"""
	def test_failure(self):
		self.assertFalse(True)
	
	def test_error(self):
		raise Exception('Something went wrong')
	
	def test_subtest_failure(self):
		with self.subTest('a succeeding subtest'):
			pass
		
		with self.subTest('a failing subtest'):
			self.test_failure()
	
	def test_subtest_error(self):
		with self.subTest('a failing subtest'):
			self.test_failure()
		
		with self.subTest('an erroring subtest'):
			self.test_error()


class TestRunner(unittest.TestCase):
	def setUp(self):
		self.capture = StringIO()
		self.runner = JSONTestRunner(self.capture)
	
	def run_test(self, name: str, typ: str, id_: str, desc: Optional[str], msg_re: Union[str, re_t.Pattern]):
		self.runner.run(unittest.defaultTestLoader.loadTestsFromName('tests.TestsToBeTested.{}'.format(name)))
		v = self.capture.getvalue()
		self.assertTrue(v, 'no JSON received')
		for v in v.split('\n'):
			result = json.loads(v)
			
			self.assertSetEqual(set(result.keys()), {'type', 'id', 'desc', 'msg'})
			result = StructuredResult(**result)
			self.assertEqual(result.type, typ)
			self.assertEqual(result.id, id_)
			self.assertEqual(result.desc, desc)
			self.assertRegex(result.msg, re.compile(msg_re, re.DOTALL))
			return result
	
	def test_failure(self):
		self.run_test(
			'test_failure',
			'failure',
			'tests.TestsToBeTested.test_failure',
			None,
			r'^Traceback.*in test_failure.*AssertionError: True is not false\n$')
	
	def test_error(self):
		self.run_test(
			'test_error',
			'error',
			'tests.TestsToBeTested.test_error',
			None,
			r'^Traceback.*in test_error.*Exception: Something went wrong\n$')
	
	def test_subtest_failure(self):
		self.run_test(
			'test_subtest_failure',
			'error',
			'tests.TestsToBeTested.test_subtest_failure',
			None,
			r'^Traceback.*in test_subtest_failure.*Exception: Something went wrong\n$')


def load_tests(loader: unittest.TestLoader, standard_tests: unittest.TestSuite, pattern: Optional[str]):
	return unittest.TestSuite(loader.loadTestsFromTestCase(TestRunner))

if __name__ == '__main__':
	unittest.main()
