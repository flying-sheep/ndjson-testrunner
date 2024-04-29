from __future__ import annotations

import sys
import unittest

from . import JSONTestRunner

module = sys.argv[1]
sys.argv[1:] = sys.argv[2:]
unittest.main(module, testRunner=JSONTestRunner)
