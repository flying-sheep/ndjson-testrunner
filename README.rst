ndjson TestRunner |pypi-badge|
==============================

Exports `JSONTestRunner`, a unittest_ ``TestRunner`` class that outputs ndjson_. One JSON record per test result:

.. code-block:: javascript

	{
		"type": "success" | "expected_failure" | "failure" | "error" | "unexpected_success" | "skip",
		"id":   "module.TestClass.test_function",
		"desc": null | "First line of test function docstring",
		"msg":  null | "Exception traceback or reason for skipping"
	}

To be used for test result storage or interprocess communication.

Usage
-----

Use it programmatically:

>>> import unittest
>>> from ndjson_testrunner import JSONTestRunner
>>> unittest.main("test_module_name", testRunner=JSONTestRunner)

or from the command line:

.. code-block:: bash

   python -m ndjson_testrunner test_module_name

Check out e.g. how `IRKernel’s usage`_ looks.

.. _unittest: https://docs.python.org/3/library/unittest.html
.. _ndjson: http://ndjson.org
.. _IRKernel’s usage: https://github.com/IRkernel/IRkernel/blob/master/tests/testthat/test_kernel.r

.. |pypi-badge| image:: https://img.shields.io/pypi/v/ndjson-testrunner.svg?style=flat-square
	:target: https://pypi.python.org/pypi/ndjson-testrunner
