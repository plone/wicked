"""
"""
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

def test_suite():
    import unittest
    from Products.wicked.lib.filtercore import setup, FilterCacheChecker, cache, query
    from Products.wicked.lib.testing.filtercore import dummy, fakecacheiface, fakefilter
    import doctest
    # filter core needs it's own txt....this does not resolve
    return unittest.TestSuite((
        doctest.DocFileSuite('filtercore.py', package="Products.wicked.lib.filtercore")
        ))

if __name__ == '__main__':
    framework()
