import os, sys
import unittest
from sets import Set
import traceback

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from wickedtestcase import WickedTestCase, test_content
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

    def testLinkPriorities(self):
        self.createRichTestContent()

        wf1 = self.folder.wf1
        wf2 = self.folder.wf2
        wf3 = self.folder.wf3
        
        wf1_wicked1 = getattr(wf1, 'wicked-one')
        wf1_wicked2 = getattr(wf1, 'wicked-two')
        wf1_wicked3 = getattr(wf1, 'wicked-three')

        wf2_wicked1 = getattr(wf2, 'wicked-one')
        wf2_wicked2_diffid = getattr(wf2, 'wicked-two-diff-id')
        wf2_wicked3_difftitle = getattr(wf2, 'wicked-three')

        wf3_wicked1 = getattr(wf3, 'wicked-one')
        wf3_wicked2 = getattr(wf3, 'wicked-two')

        wf1_wicked1.setBody("((%s)) ((%s))" % (wf1_wicked2.id, wf1_wicked3.id))
        self.failUnless(self.hasWickedLink(wf1_wicked1, wf1_wicked2))
        self.failUnless(self.hasWickedLink(wf1_wicked1, wf1_wicked3))

        wf1_wicked1.setBody("((%s)) ((%s))" % (wf1_wicked2.Title(),
                                               wf1_wicked3.Title()))
        self.failUnless(self.hasWickedLink(wf1_wicked1, wf1_wicked2))
        self.failUnless(self.hasWickedLink(wf1_wicked1, wf1_wicked3))

        wf1_wicked2.setBody("((%s))" % wf1_wicked1.id)
        self.failUnless(self.hasWickedLink(wf1_wicked2, wf1_wicked1))

        wf1_wicked2.setBody("((%s))" % wf1_wicked1.Title())
        self.failUnless(self.hasWickedLink(wf1_wicked2, wf1_wicked1))

        wf2_wicked2_diffid.setBody("((%s))" % wf2_wicked1.id)
        self.failUnless(self.hasWickedLink(wf2_wicked2_diffid,
                                           wf2_wicked1))

        wf2_wicked2_diffid.setBody("((%s))" % wf2_wicked1.Title())
        self.failUnless(self.hasWickedLink(wf2_wicked2_diffid,
                                           wf2_wicked1))

        wf1_wicked1.setBody("((%s))" % wf2_wicked2_diffid.id)
        self.failUnless(self.hasWickedLink(wf1_wicked1, wf2_wicked2_diffid))

        
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
