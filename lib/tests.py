def test_suite():
    import unittest, doctest
    from Testing.ZopeTestCase import ZopeDocFileSuite
    from collective.testing.layer import ZCMLLayer
    from Products.wicked.lib.utils import test_suite as utilsuite

    cachemanager = ZopeDocFileSuite('cache.txt',
                                    package='Products.wicked.lib',
                                    optionflags = doctest.REPORT_ONLY_FIRST_FAILURE | doctest.ELLIPSIS)
    cachemanager.layer = ZCMLLayer
    utils = utilsuite()
    return unittest.TestSuite((utils, cachemanager))
