try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

def readme():
	with open('README.rst') as f:
		return f.read()

setup(
	name='ndjson-testrunner',
	version='1.0.0',
	description='A test runner that outputs newline delimited JSON results',
	long_description=readme(),
	classifiers=[
		'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
		'Programming Language :: Python :: 3',
		'Topic :: Software Development :: Testing',
	],
	py_modules=['ndjson_testrunner'],
	url='https://flying-sheep.github.io/ndjson-testrunner',
	license='GPLv3+',
	author='Philipp A',
	author_email='flying-sheep@web.de',
	test_suite='tests',
)
