from zope.testing import doctest
optionflags = doctest.REPORT_ONLY_FIRST_FAILURE | doctest.ELLIPSIS
from collective.testing.layer import ZCMLLayer

def test_suite():
    import unittest
    from Products.ATContentTypes.tests.atcttestcase import ATCTFunctionalSiteTestCase 
    from Testing.ZopeTestCase import FunctionalDocFileSuite, ZopeDocFileSuite
    suites = (FunctionalDocFileSuite('add.txt',
                                    package='Products.wicked.browser',
                                    test_class=ATCTFunctionalSiteTestCase,                                   
                                    optionflags=optionflags),
              ZopeDocFileSuite('renderer.txt',
                               package='Products.wicked.browser',
                               optionflags=optionflags))

    [setattr(suite, 'layer', ZCMLLayer) for suite in suites]
    return unittest.TestSuite(suites)
