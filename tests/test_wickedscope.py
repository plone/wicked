import os, sys, time
import unittest
from sets import Set
import traceback

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase

from Products.wicked.lib.normalize import titleToNormalizedId
from Products.wicked.config import BACKLINK_RELATIONSHIP
from Products.wicked.example import WickedDoc
from wickedtestcase import WickedTestCase, makeContent


def scopeTester(self):
    """
    a demo scope method for testing, returns a scope that includes
    the parent of the current container, but not anything two levels
    (or more) up
    """
    scope_obj = self.aq_inner.aq_parent
    if not self.isPrincipiaFolderish:
        scope_obj = scope_obj.aq_inner.aq_parent
    path = '/'.join(scope_obj.getPhysicalPath())
    return path

class TestWickedScope(WickedTestCase):
    wicked_type = 'WickedDoc'
    wicked_field = 'text'

    def afterSetUp(self):
        WickedDoc.scopeTester = scopeTester
        WickedDoc.schema['text'].scope = 'scopeTester'
        WickedTestCase.afterSetUp(self)

    def beforeTearDown(self):
        del WickedDoc.scopeTester
        WickedDoc.schema['text'].scope = ''

    def test_insideScope(self):
        f2 = makeContent(self.folder, 'f2', 'Folder')
        wd1 = makeContent(f2, 'wd1', 'WickedDoc',
                          title='WD1 Title')
        wd1.setText("((%s))" % self.page1.Title())
        self.failUnless(self.hasWickedLink(wd1, self.page1))

    def test_outsideScope(self):
        f2 = makeContent(self.folder, 'f2', 'Folder')
        f3 = makeContent(f2, 'f3', 'Folder')
        wd1 = makeContent(f3, 'wd1', 'WickedDoc',
                          title='WD1 Title')
        wd1.setText("((%s))" % self.page1.Title())
        self.failIf(self.hasWickedLink(wd1, self.page1))
        

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestWickedScope))
    return suite

if __name__ == '__main__':
    framework()
