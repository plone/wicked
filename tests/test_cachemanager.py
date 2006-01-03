"""
"""
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

def test_suite():
    import unittest
    
    from Testing.ZopeTestCase import ZopeDocFileSuite
    from Testing.ZopeTestCase import ZopeDocTestSuite

    return unittest.TestSuite((
        ZopeDocFileSuite('cache.txt', package='Products.wicked.lib'),
        ZopeDocTestSuite('Products.wicked.lib.factories')
        ))

if __name__ == '__main__':
    framework()
