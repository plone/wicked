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

    def replaceCreatedWithFieldIndex(self):
        """ replace the 'created' index w/ a field index b/c we need
        better than 1 minute resolution for our testing """
        cat = self.portal.portal_catalog
        cat.delIndex('created')
        cat.manage_addIndex('created', 'FieldIndex',
                            extras={indexed_attrs:'created'})
        cat.manage_reindexIndex(ids=['created'])

    def test_backlink(self):
        assert self.page1 in self.page2.getRefs(relationship=BACKLINK_RELATIONSHIP)

    def testforlink(self):
        self.failUnless(self.hasWickedLink(self.page1, self.page2))

    def testformultiplelinks(self):
        self.page1.setBody('((DMV Computer has died))  ((Make another link))')
        self.failUnless(self.hasAddLink(self.page1))
        self.failUnless(self.hasWickedLink(self.page1, self.page2))

    def testLocalIdBeatsLocalTitle(self):
        w1 = makeContent(self.folder, 'IdTitleClash',
                         'IronicWiki', title='Some Title')
        w2 = makeContent(self.folder, 'some_other_id',
                         'IronicWiki', title='IdTitleClash')
        self.page1.setBody("((%s))" % w1.id) # matches w2 title
        self.failUnless(self.hasWickedLink(self.page1, w1))
        self.failIf(self.hasWickedLink(self.page1, w2))

    def testLocalIdBeatsRemoteId(self):
        f2 = makeContent(self.folder, 'f2', 'Folder')
        w1 = makeContent(f2, self.page1.id, 'IronicWiki',
                         title='W1 Title')
        w2 = makeContent(f2, 'w2_id', 'IronicWiki',
                         title='W2 Title')
        w2.setBody("((%s))" % self.page1.id)
        self.failUnless(self.hasWickedLink(w2, w1))
        self.failIf(self.hasWickedLink(w2, self.page1))

    def testLocalTitleBeatsRemoteId(self):
        f2 = makeContent(self.folder, 'f2', 'Folder')
        w1 = makeContent(f2, 'w1_id', 'IronicWiki',
                         title=self.page1.id)
        w2 = makeContent(f2, 'w2_id', 'IronicWiki',
                         title='W2 Title')
        w2.setBody("((%s))" % self.page1.id)
        self.failUnless(self.hasWickedLink(w2, w1))
        self.failIf(self.hasWickedLink(w2, self.page1))
        
    def testInexactTitleNotMatch(self):
        w1 = makeContent(self.folder, 'w1', 'IronicWiki',
                         title='W1 Title With Extra')
        self.page1.setBody("((W1 Title))")
        self.failIf(self.hasWickedLink(self.page1, w1))
        self.failUnless(self.hasAddLink(self.page1))

    def testInexactTitleNotBlockLocalId(self):
        w1 = makeContent(self.folder, 'w1', 'IronicWiki',
                         title='W1 Title')
        w2 = makeContent(self.folder, 'w2', 'IronicWiki',
                         title='%s With Extra' % w1.id)
        self.page1.setBody("((%s))" % w1.id)
        self.failUnless(self.hasWickedLink(self.page1, w1))
        self.failIf(self.hasWickedLink(self.page1, w2))

    def testInexactLocalTitleNotBlockLocalTitle(self):
        w1 = makeContent(self.folder, 'w1', 'IronicWiki',
                         title='W1 Title')
        w2 = makeContent(self.folder, 'w2', 'IronicWiki',
                         title='%s With Extra' % w1.Title())
        self.page1.setBody("((%s))" % w1.Title())
        self.failUnless(self.hasWickedLink(self.page1, w1))
        self.failIf(self.hasWickedLink(self.page1, w2))

    def testInexactLocalTitleNotBlockRemoteId(self):
        f2 = makeContent(self.folder, 'f2', 'Folder')
        w1 = makeContent(self.folder, 'w1', 'IronicWiki',
                         title='W1 Title')
        w2 = makeContent(f2, 'w2', 'IronicWiki',
                         title='%s With Extra' % w1.id)
        w3 = makeContent(f2, 'w3', 'IronicWiki',
                         title='W3 Title')
        w3.setBody("((%s))" % w1.id)
        self.failUnless(self.hasWickedLink(w3, w1))
        self.failIf(self.hasWickedLink(w3, w2))

    def testInexactRemoteTitleNotBlockRemoteId(self):
        f2 = makeContent(self.folder, 'f2', 'Folder')
        w1 = makeContent(self.folder, 'w1', 'IronicWiki',
                         title='W1 Title')
        w2 = makeContent(self.folder, 'w2', 'IronicWiki',
                         title='%s With Extra' % w1.id)
        w3 = makeContent(f2, 'w3', 'IronicWiki',
                         title='W3 Title')
        w3.setBody("((%s))" % w1.id)
        self.failUnless(self.hasWickedLink(w3, w1))
        self.failIf(self.hasWickedLink(w3, w2))

    def testInexactLocalTitleNotBlockRemoteTitle(self):
        f2 = makeContent(self.folder, 'f2', 'Folder')
        w1 = makeContent(self.folder, 'w1', 'IronicWiki',
                         title='W1 Title')
        w2 = makeContent(f2, 'w2', 'IronicWiki',
                         title='%s With Extra' % w1.Title())
        w3 = makeContent(f2, 'w3', 'IronicWiki',
                         title='W3 Title')
        w3.setBody("((%s))" % w1.Title())
        self.failUnless(self.hasWickedLink(w3, w1))
        self.failIf(self.hasWickedLink(w3, w2))

    def testInexactRemoteTitleNotBlockRemoteTitle(self):
        f2 = makeContent(self.folder, 'f2', 'Folder')
        w1 = makeContent(self.folder, 'w1', 'IronicWiki',
                         title='W1 Title')
        w2 = makeContent(self.folder, 'w2', 'IronicWiki',
                         title='%s With Extra' % w1.Title())
        w3 = makeContent(f2, 'w3', 'IronicWiki',
                         title='W3 Title')
        w3.setBody("((%s))" % w1.Title())
        self.failUnless(self.hasWickedLink(w3, w1))
        self.failIf(self.hasWickedLink(w3, w2))

    def testDuplicateLocalTitleMatchesOldest(self):
        title = 'Duplicate Title'
        w1 = makeContent(self.folder, 'w1', 'IronicWiki',
                         title=title)
        w2 = makeContent(self.folder, 'w2', 'IronicWiki',
                         title=title)
        w3 = makeContent(self.folder, 'w3', 'IronicWiki',
                         title=title)
        self.page1.setBody("((%s))" % title)
        self.failUnless(self.hasWickedLink(self.page1, w1))
        self.failIf(self.hasWickedLink(self.page1, w2))
        self.failIf(self.hasWickedLink(self.page1, w3))

        self.folder.manage_delObjects(ids=[w1.id])
        self.failUnless(self.hasWickedLink(self.page1, w2))
        self.failIf(self.hasWickedLink(self.page1, w3))
        

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
