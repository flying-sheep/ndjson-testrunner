ndjson TestRunner
=================

A unittest_ ``TestRunner`` that outputs ndjson_. One JSON record per test result::

	{
		"type": "success" | "expected_failure" | "failure" | "error" | "unexpected_success" | "skip",
		"id":   "module.TestClass.test_function",
		"desc": null | "First line of test function docstring",
		"msg":  null | "Exception traceback or reason for skipping"
	}

To be used for test result storage or interprocess communication.

.. _unittest: https://docs.python.org/3/library/unittest.html
.. _ndjson: http://ndjson.org
