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

    def hasAddLink(self, doc):
        """ does doc body contain a wicked-generated add link? """
        # XXX make test stronger, support looking for specifc links
        return doc.absolute_url() in doc.getBody()

    def hasWickedLink(self, doc, dest):
        """ does doc body contain a resolved wicked link to the specified
        dest object? """
        # XXX make test stronger
        return dest.absolute_url() in doc.getBody()

    def test_backlink(self):
        assert self.page1 in self.page2.getRefs(relationship=BACKLINK_RELATIONSHIP)

    def testforlink(self):
        self.failUnless(self.hasWickedLink(self.page1, self.page2))

    def testformultiplelinks(self):
        self.page1.setBody('((DMV Computer has died))  ((Make another link))')
        self.failUnless(self.hasAddLink(self.page1))
        self.failUnless(self.hasWickedLink(self.page1, self.page2))

class TestDocCreation(WickedTestCase):
    def afterSetUp(self):
        WickedTestCase.afterSetUp(self)
        self.title = 'Create a New Document'
        self.page1.setBody('((%s))' %self.title)
        self._refreshSkinData()

    def demoCreate(self):
        self.login('test_user_1_')
        self.page1.addByWickedLink(Title=self.title)
        
    def testDocAdded(self):
        self.demoCreate()
        self.failUnless(getattr(self.folder,
                                titleToNormalizedId(self.title), None))

    def testBacklinks(self):
        self.demoCreate()
        newdoc = getattr(self.folder, titleToNormalizedId(self.title))
        backlinks = newdoc.getRefs(relationship=BACKLINK_RELATIONSHIP)
        self.failUnless(self.page1 in backlinks)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDocCreation))
    suite.addTest(unittest.makeSuite(TestWikiLinking))
    return suite

if __name__ == '__main__':
    framework()
