import os, sys, unittest

base = "../lib"
try: base = os.path.abspath(os.path.join(os.path.dirname(__file__), base))
except: pass

sys.path.insert(0, base)

from filtercore import test_suite
if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())

