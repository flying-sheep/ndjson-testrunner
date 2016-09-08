try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

setup(
	name='ndjson-testrunner',
	version='1.0.0',
	py_modules=['ndjson_testrunner'],
	url='https://flying-sheep.github.io/ndjson-testrunner',
	license='GPL',
	author='Philipp A',
	author_email='flying-sheep@web.de',
	description='A test runner that outputs newline delimited JSON results',
	test_suite='tests',
)
