from __future__ import annotations

import json
import re
import unittest
from io import StringIO
from typing import TYPE_CHECKING, cast, overload

from ndjson_testrunner import JSONTestRunner, TestResultDict

if TYPE_CHECKING:
    from typing import Literal, Never


class TestsToBeTested(unittest.TestCase):
    """Those tests are not there to pass, but to create all kinds of output"""

    def test_success(self) -> None:
        self.assertTrue(True)

    def test_failure(self) -> None:
        self.assertFalse(True)

    def test_error(self) -> Never:
        raise Exception("Something went wrong")

    def test_subtest_success(self) -> None:
        with self.subTest("a succeeding subtest"):
            pass

    def test_subtest_failure(self) -> None:
        with self.subTest("a failing subtest"):
            self.test_failure()

        with self.subTest("an erroring subtest"):
            self.test_error()


class TestRunner(unittest.TestCase):
    def setUp(self) -> None:
        self.capture = StringIO()
        self.runner = JSONTestRunner(self.capture)

    @overload
    def run_test(self, name: str, subtests: Literal[False] = False) -> TestResultDict: ...

    @overload
    def run_test(self, name: str, subtests: Literal[True]) -> map[TestResultDict]: ...

    def run_test(self, name: str, subtests: bool = False) -> TestResultDict | map[TestResultDict]:
        self.runner.run(unittest.defaultTestLoader.loadTestsFromName(f"tests.TestsToBeTested.{name}"))
        v = self.capture.getvalue()
        self.assertTrue(v, "no JSON received")
        if subtests:
            return map(json.loads, v.strip().split("\n"))
        else:
            self.assertNotIn("\n", v.strip(), "expected 1 ndjson record")
            return cast(TestResultDict, json.loads(v))

    def check_test(
        self, test: str | TestResultDict, typ: str, id_: str, desc: str | None, msg_re: str | re.Pattern[str] | None
    ) -> TestResultDict:
        result = self.run_test(test) if isinstance(test, str) else test
        self.assertSetEqual(set(result.keys()), {"type", "id", "desc", "msg"})
        self.assertEqual(result["type"], typ)
        self.assertEqual(result["id"], id_)
        self.assertEqual(result["desc"], desc)
        if result["msg"] is not None:
            assert msg_re is not None
            self.assertRegex(result["msg"], re.compile(msg_re, re.DOTALL))
        return result

    def test_success(self) -> None:
        """Test a normal succeeding tests"""
        self.check_test("test_success", "success", "tests.TestsToBeTested.test_success", None, None)

    def test_failure(self) -> None:
        """Test a normal failing tests"""
        self.check_test(
            "test_failure",
            "failure",
            "tests.TestsToBeTested.test_failure",
            None,
            r"^Traceback.*in test_failure.*AssertionError: True is not false\n$",
        )

    def test_error(self) -> None:
        self.check_test(
            "test_error",
            "error",
            "tests.TestsToBeTested.test_error",
            None,
            r"^Traceback.*in test_error.*Exception: Something went wrong\n$",
        )

    def test_subtest_success(self) -> None:
        """Test if subtests result in the whole thing to pass"""
        succ_sub, succ_total = self.run_test("test_subtest_success", subtests=True)
        self.check_test(
            succ_sub, "success", "tests.TestsToBeTested.test_subtest_success [a succeeding subtest]", None, None
        )
        self.check_test(succ_total, "success", "tests.TestsToBeTested.test_subtest_success", None, None)

    def test_subtest_failure(self) -> None:
        """Test if all subtests run"""
        fail, error = self.run_test("test_subtest_failure", subtests=True)
        self.check_test(
            fail,
            "failure",
            "tests.TestsToBeTested.test_subtest_failure [a failing subtest]",
            None,
            r"^Traceback.*in test_subtest_failure.*AssertionError: True is not false\n$",
        )
        self.check_test(
            error,
            "error",
            "tests.TestsToBeTested.test_subtest_failure [an erroring subtest]",
            None,
            r"^Traceback.*in test_error.*Exception: Something went wrong\n$",
        )


def load_tests(
    loader: unittest.TestLoader, standard_tests: unittest.TestSuite, pattern: str | None
) -> unittest.TestSuite:
    return unittest.TestSuite(loader.loadTestsFromTestCase(TestRunner))
