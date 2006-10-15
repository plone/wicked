import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

def test_suite():
    import unittest
    from Testing.ZopeTestCase import ZopeDocFileSuite

    return unittest.TestSuite((
        ZopeDocFileSuite('cache.txt', package='Products.wicked.lib'),
        ))

if __name__ == '__main__':
    framework()
