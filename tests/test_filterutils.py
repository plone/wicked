import os
import sys
import unittest

base = "../lib"
try: base = os.path.abspath(os.path.join(os.path.dirname(__file__), base))
except: pass

sys.path.insert(0, base)

from utils import test_suite as util_suite
from normalize import NormTestCase

def test_suite():
    return unittest.TestSuite((util_suite(), unittest.makeSuite(NormTestCase)))

if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite)

