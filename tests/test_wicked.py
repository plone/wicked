import os, sys
import unittest
from sets import Set
import traceback

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from wickedtestcase import WickedTestCase
from Products.wicked.lib.normalize import titleToNormalizedId
from Products.wicked.config import BACKLINK_RELATIONSHIP

class TestWikiLinking(WickedTestCase):
    def afterSetUp(self):
        WickedTestCase.afterSetUp(self)
        self.page1.setBody('((DMV Computer has died))')

    def test_backlink(self):
        assert self.page1 in self.page2.getRefs(relationship=BACKLINK_RELATIONSHIP)

    def testforlink(self):
        assert self.page1.absolute_url() in self.page1.getBody()

    def testformultiplelinks(self):
        self.page1.setBody('((DMV Computer has died))  ((Make another link))')
        assert self.page1.absolute_url() in self.page1.getBody()

class TestDocCreation(WickedTestCase):
    def afterSetUp(self):
        WickedTestCase.afterSetUp(self)
        self.title = 'Create a New Document'
        self.page1.setBody('((%s))' %self.title)
        self._refreshSkinData()

    def demoCreate(self):
        self.login('test_user_1_')
        self.page1.addByWickedLink(Title=self.title, type_name='Document')
        
    def testDocAdded(self):
        self.demoCreate()
        self.failUnless(getattr(self.folder, titleToNormalizedId(self.title), None))

    def testBacklinks(self):
        self.demoCreate()
        newdoc = getattr(self.folder, titleToNormalizedId(self.title))
        self.failUnless(self.page1 in newdoc.getRefs(relationship=BACKLINK_RELATIONSHIP))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDocCreation))
    suite.addTest(unittest.makeSuite(TestWikiLinking))
    return suite

if __name__ == '__main__':
    framework()
