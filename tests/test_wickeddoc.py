import os, sys, time
import unittest
from sets import Set
import traceback

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from wickedtestcase import WickedTestCase, makeContent
from Products.wicked.lib.normalize import titleToNormalizedId
from Products.wicked.config import BACKLINK_RELATIONSHIP


class TestWickedDoc(WickedTestCase):
    wicked_type = 'WickedDoc'
    wicked_field = 'text'

    def test_filterApplied(self):
        wd1 = makeContent(self.folder, 'wd1', 'WickedDoc',
                              title='WD1 Title')
        wd1.setText("((%s)) ((%s))" % (self.page1.Title(),
                                       "Nonexistent Title"))
        self.failUnless(self.hasWickedLink(wd1, self.page1))
        self.failUnless(self.hasAddLink(wd1))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestWickedDoc))
    return suite

if __name__ == '__main__':
    framework()
