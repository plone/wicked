import os, sys, time
import unittest
from sets import Set
import traceback

from Testing import ZopeTestCase
from wickedtestcase import WickedTestCase, makeContent
from wicked.normalize import titleToNormalizedId
from wicked.config import BACKLINK_RELATIONSHIP

has_atct = True
try:
    from Products import ATContentTypes
except ImportError:
    print "WARNING: ATContentTypes not installed, WickedDoc tests not running"
    has_atct = False

class TestWickedDoc(WickedTestCase):
    wicked_type = 'WickedDoc'
    wicked_field = 'text'

    def test_filterApplied(self):
        wd1 = makeContent(self.folder, 'wd1', 'WickedDoc',
                              title='WD1 Title')
        wd1.setText("((%s)) ((%s))" % (self.page1.Title(),
                                       "Nonexistent Title"))
        self.failUnlessWickedLink(wd1, self.page1)
        self.failUnlessAddLink(wd1)

def test_suite():
    suite = unittest.TestSuite()
    if has_atct:
        suite.addTest(unittest.makeSuite(TestWickedDoc))
    return suite


