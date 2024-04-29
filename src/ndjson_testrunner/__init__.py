from __future__ import annotations

import json
import sys
import unittest
import warnings
from contextlib import contextmanager
from dataclasses import InitVar, dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Literal, TextIO, TypedDict

if TYPE_CHECKING:
    from collections.abc import Generator

    from _typeshed import OptExcInfo

__all__ = ["JSONTestResult", "JSONTestRunner", "TestResultType", "TestResultDict"]


TestResultType = Literal["success", "failure", "error", "skip", "expected_failure", "unexpected_success"]


class TestResultDict(TypedDict):
    type: TestResultType
    id: str
    desc: str | None
    msg: str | None


class JSONTestResult(unittest.TestResult):
    def __init__(self, stream: TextIO, failfast: bool, buffer: bool, tb_locals: bool) -> None:
        super().__init__(stream)
        self.stream = stream
        self.failfast = failfast
        self.buffer = buffer
        self.tb_locals = tb_locals

    _exc_info_to_string: Callable[[Any, unittest.TestCase], str]

    def test_run(self, test: unittest.TestSuite | unittest.TestCase) -> None:
        self.startTestRun()
        try:
            test(self)
        finally:
            self.stopTestRun()

    def result_to_dict(
        self, type_: TestResultType, test: unittest.TestCase, err_or_reason: OptExcInfo | str | None = None
    ) -> TestResultDict:
        msg = None
        if isinstance(err_or_reason, tuple) and len(err_or_reason) == 3:
            msg = self._exc_info_to_string(err_or_reason, test)
        elif err_or_reason:
            msg = str(err_or_reason)

        return TestResultDict(
            type=type_,
            id=test.id(),
            desc=test.shortDescription(),  # May be None
            msg=msg,
        )

    def write_result(
        self, typ_: TestResultType, test: unittest.TestCase, err_or_reason: OptExcInfo | str | None = None
    ) -> None:
        json.dump(self.result_to_dict(typ_, test, err_or_reason), self.stream, separators=(",", ":"))
        self.stream.write("\n")

    def addSuccess(self, test: unittest.TestCase) -> None:
        super().addSuccess(test)
        self.write_result("success", test)

    def addExpectedFailure(self, test: unittest.TestCase, err: OptExcInfo) -> None:
        super().addExpectedFailure(test, err)
        self.write_result("expected_failure", test, err)

    def addFailure(self, test: unittest.TestCase, err: OptExcInfo) -> None:
        super().addFailure(test, err)
        self.write_result("failure", test, err)

    def addError(self, test: unittest.TestCase, err: OptExcInfo) -> None:
        super().addError(test, err)
        self.write_result("error", test, err)

    def addUnexpectedSuccess(self, test: unittest.TestCase) -> None:
        super().addUnexpectedSuccess(test)
        self.write_result("unexpected_success", test)

    def addSkip(self, test: unittest.TestCase, reason: str) -> None:
        super().addSkip(test, reason)
        self.write_result("skip", test, reason)

    def addSubTest(self, test: unittest.TestCase, subtest: unittest.TestCase, err: OptExcInfo | None) -> None:
        super().addSubTest(test, subtest, err)
        if err is None:
            self.write_result("success", subtest)
        elif err[0] and issubclass(err[0], test.failureException):
            self.write_result("failure", subtest, err)
        else:
            self.write_result("error", subtest, err)


WarningAction = Literal["default", "error", "ignore", "always", "module", "once"]


@dataclass
class JSONTestRunner:
    """TODO"""

    _stream: InitVar[TextIO | None] = field(default=None, repr=False)
    failfast: bool = False
    buffer: bool = False
    warnings: WarningAction | None = None

    if sys.version_info < (3, 10):
        tb_locals: bool = field(default=False)
    else:
        tb_locals: bool = field(default=False, kw_only=True)

    stream: TextIO = field(init=False)

    def __post_init__(self, _stream: TextIO | None) -> None:
        """Construct a JSONTestRunner."""
        self.stream = sys.stdout if _stream is None else _stream

    @contextmanager
    def filter_warnings(self) -> Generator[None, None, None]:
        """Install own warnings filter for the context"""
        with warnings.catch_warnings():
            if self.warnings:
                warnings.simplefilter(self.warnings)
                if self.warnings in ["default", "always"]:
                    warnings.filterwarnings(
                        "module", category=DeprecationWarning, message=r"Please use assert\w+ instead."
                    )
            yield

    def run(self, test: unittest.TestSuite | unittest.TestCase) -> JSONTestResult:
        """Run the given test case or test suite."""
        result = JSONTestResult(self.stream, self.failfast, self.buffer, self.tb_locals)
        unittest.registerResult(result)
        with self.filter_warnings():
            result.test_run(test)
        return result
