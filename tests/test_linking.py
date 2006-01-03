import os, sys, time
import unittest
from sets import Set
import traceback

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from wickedtestcase import WickedTestCase, makeContent, TITLE2
from Products.wicked.lib.normalize import titleToNormalizedId
from Products.wicked.config import BACKLINK_RELATIONSHIP
from Products.CMFCore.utils import getToolByName

class Base(WickedTestCase):
    wicked_type = 'IronicWiki'
    wicked_field = 'body'
    
    def demoCreate(self, **kw):
        self.login('test_user_1_')
        self.page1.addByWickedLink(Title=kw.get('Title', self.title))

class TestWikiLinking(Base):
    wicked_type = 'IronicWiki'
    wicked_field = 'body'
    
    def afterSetUp(self):
        super(TestWikiLinking, self).afterSetUp()
        self.page1.setBody('((%s))' % TITLE2)

    def replaceCreatedIndex(self):
        """ replace the 'created' index w/ a field index b/c we need
        better than 1 minute resolution for our testing """
        cat = getToolByName(self.portal, 'portal_catalog')
        cat.delIndex('created')
        cat.manage_addIndex('created', 'FieldIndex',
                            extra={'indexed_attrs':'created'})
        cat.manage_reindexIndex(ids=['created'])

    def test_backlink(self):
        assert self.page1 in self.page2.getRefs(relationship=BACKLINK_RELATIONSHIP)

    def testforlink(self):
        self.failUnlessWickedLink(self.page1, self.page2)

    def testformultiplelinks(self):
        self.page1.setBody('((DMV Computer has died))  ((Make another link))')
        self.failUnlessAddLink(self.page1)
                        
        self.failUnlessWickedLink(self.page1, self.page2)

##     def testLocalIdBeatsLocalTitle(self):
##         # XXX not sure about this usecase
##         # using arbritrary system ids falls more under
##         # kupu's linking capabilities, or raw stx
##         # if someone thinks matching non-autogenerated
##         # ids is important, we could add a literal syntax
##         # like maybe single quotes ''
        
##         w1 = makeContent(self.folder, 'IdTitleClash',
##                          self.wicked_type, title='Some Title')
##         w2 = makeContent(self.folder, 'some_other_id',
##                          self.wicked_type, title='IdTitleClash')
##         self.page1.setBody("((%s))" % w1.geId()) # matches w2 title
##         self.failUnlessWickedLink(self.page1, w1)
##         self.failIfWickedLink(self.page1, w2)


        
    def testInexactTitleNotMatch(self):
        w1 = makeContent(self.folder, 'w1', self.wicked_type,
                         title='W1 Title With Extra')
        self.page1.setBody("((W1 Title))")
        self.failIfWickedLink(self.page1, w1)
        self.failUnlessAddLink(self.page1)

    def testInexactTitleNotBlockLocalId(self):
        w1 = makeContent(self.folder, 'w1', self.wicked_type,
                         title='W1 Title')
        w2 = makeContent(self.folder, 'w2', self.wicked_type,
                         title='%s With Extra' % w1.id)
        self.page1.setBody("((%s))" % w1.id)
        self.failUnlessWickedLink(self.page1, w1)
        self.failIfWickedLink(self.page1, w2)

    def testInexactLocalTitleNotBlockLocalTitle(self):
        w1 = makeContent(self.folder, 'w1', self.wicked_type,
                         title='W1 Title')
        w2 = makeContent(self.folder, 'w2', self.wicked_type,
                         title='%s With Extra' % w1.Title())
        self.page1.setBody("((%s))" % w1.Title())
        self.failUnlessWickedLink(self.page1, w1)
        self.failIfWickedLink(self.page1, w2)

    def testInexactRemoteTitleNotBlockRemoteId(self):
        f2 = makeContent(self.folder, 'f2', 'Folder')
        w1 = makeContent(self.folder, 'w1', self.wicked_type,
                         title='W1 Title')
        w2 = makeContent(self.folder, 'w2', self.wicked_type,
                         title='%s With Extra' % w1.id)
        w3 = makeContent(f2, 'w3', self.wicked_type,
                         title='W3 Title')
        w3.setBody("((%s))" % w1.id)
        self.failUnlessWickedLink(w3, w1)
        self.failIfWickedLink(w3, w2)

    def testInexactRemoteTitleNotBlockRemoteTitle(self):
        f2 = makeContent(self.folder, 'f2', 'Folder')
        w1 = makeContent(self.folder, 'w1', self.wicked_type,
                         title='W1 Title')
        w2 = makeContent(self.folder, 'w2', self.wicked_type,
                         title='%s With Extra' % w1.Title())
        w3 = makeContent(f2, 'w3', self.wicked_type,
                         title='W3 Title')
        w3.setBody("((%s))" % w1.Title())
        self.failUnlessWickedLink(w3, w1)
        self.failIfWickedLink(w3, w2)

    def testDupLocalTitleMatchesOldest(self):
        self.replaceCreatedIndex()
        title = 'Duplicate Title'
        w1 = makeContent(self.folder, 'w1', self.wicked_type,
                         title=title)
        w2 = makeContent(self.folder, 'w2', self.wicked_type,
                         title=title)
        w3 = makeContent(self.folder, 'w3', self.wicked_type,
                         title=title)
        self.page1.setBody("((%s))" % title)
        self.failUnlessWickedLink(self.page1, w1)
        self.failIfWickedLink(self.page1, w2)
        self.failIfWickedLink(self.page1, w3)

        self.folder.manage_delObjects(ids=[w1.id])
        self.failUnlessWickedLink(self.page1, w2)
        self.failIfWickedLink(self.page1, w3)

    def testDupRemoteIdMatchesOldest(self):
        self.replaceCreatedIndex()
        id = 'duplicate_id'
        f2 = makeContent(self.folder, 'f2', 'Folder')
        f3 = makeContent(self.folder, 'f3', 'Folder')
        f4 = makeContent(self.folder, 'f4', 'Folder')
        w1 = makeContent(f2, id, self.wicked_type,
                         title='W1 Title')
        # mix up the order, just to make sure
        w3 = makeContent(f4, id, self.wicked_type,
                         title='W3 Title')
        w2 = makeContent(f3, id, self.wicked_type,
                         title='W2 Title')
        self.page1.setBody("((%s))" % id)
        self.failIfWickedLink(self.page1, w2)
        self.failIfWickedLink(self.page1, w3)
        self.failUnlessWickedLink(self.page1, w1)

        f2.manage_delObjects(ids=[w1.id])
        self.failIfWickedLink(self.page1, w2)

        # fails due to caching
        self.failUnlessWickedLink(self.page1, w3)


    def testDupRemoteTitleMatchesOldest(self):
        self.replaceCreatedIndex()
        title = 'Duplicate Title'
        f2 = makeContent(self.folder, 'f2', 'Folder')
        f3 = makeContent(self.folder, 'f3', 'Folder')
        f4 = makeContent(self.folder, 'f4', 'Folder')
        w1 = makeContent(f2, 'w1', self.wicked_type,
                         title=title)
        # mix up the order, just to make sure
        w3 = makeContent(f4, 'w3', self.wicked_type,
                         title=title)
        w2 = makeContent(f3, 'w2', self.wicked_type,
                         title=title)
        self.page1.setBody("((%s))" % title)
        self.failUnlessWickedLink(self.page1, w1)
        self.failIfWickedLink(self.page1, w2)
        self.failIfWickedLink(self.page1, w3)

        f2.manage_delObjects(ids=[w1.id])
        self.failUnlessWickedLink(self.page1, w3)
        self.failIfWickedLink(self.page1, w2)

class TestDocCreation(Base):
    
    def afterSetUp(self):
        WickedTestCase.afterSetUp(self)
        self.title = 'Create a New Document'
        self.page1.setBody('((%s))' %self.title)
        self._refreshSkinData()
        
    def testDocAdded(self):
        self.demoCreate()
        self.failUnless(getattr(self.folder,
                                titleToNormalizedId(self.title), None))

    def testBacklinks(self):
        self.demoCreate()
        newdoc = getattr(self.folder, titleToNormalizedId(self.title))
        backlinks = newdoc.getRefs(relationship=BACKLINK_RELATIONSHIP)
        self.failUnless(self.page1 in backlinks)

## from Products.PloneTestCase import setup
## import inspect
## class MetaBaseTestRemover(setup.MetaPlaceless):
##     def __init__(klass, name, bases, kdict):
##         super(MetaBaseTestRemover, klass).__init__(name, bases, kdict)
##         import pdb; pdb.set_trace()
##         methods = ((delattr(subclass, method_name) for method_name, v in inspect.getmembers(subclass, inspect.ismethod)) for subclass in klass.__subclasses__())
        
class TestLinkNormalization(Base):
    title = 'the monkey flies at dawn'

    def afterSetUp(self):
        super(TestLinkNormalization, self).afterSetUp()
        title1 = self.title 
        self.login('test_user_1_')
        self.newpage = self.clickCreate(self.page1, self.title)

    def clickCreate(self, page, title):
        page.addByWickedLink(Title=title)
        # oldbody = page.getBody(raw=True)

        page.setBody("((%s))" %title )
        return getattr(self.folder, titleToNormalizedId(title))
        
    def test_oldWinsNew(self):
        newtitle = 'I changed my mind'
        self.page2.update(**dict(title=self.title))
        self.newpage.update(**dict(title=newtitle))

        # page one should still link to new page
        # even though page2 has same title as link
        self.failUnlessWickedLink(self.page1, self.newpage)

        # delete newpage and recreate
        # older title should beat newer id
        self.loginAsPortalOwner()
        self.folder.manage_delObjects([self.newpage.getId()])
        self.newpage = self.clickCreate(self.page2, self.title)

        self.failUnlessWickedLink(self.page1, self.page2)
        self.failIfWickedLink(self.page1, self.newpage)

        
    def test_create_titlechange(self):
        # add content from link
        # test link
        # change title
        # test link
        title1 = self.title 

        # if this fail, wicked is not working period
        self.failUnlessWickedLink(self.page1, self.newpage)

        self.newpage.update(**dict(title='I changed my mind'))
        self.failUnlessWickedLink(self.page1, self.newpage)

class TestRemoteLinking(Base):
    wicked_type = 'IronicWiki'
    wicked_field = 'body'
    
    def afterSetUp(self):
        super(TestRemoteLinking, self).afterSetUp()
        self.page1.setBody('((%s))' % TITLE2)

    def testLocalIdBeatsRemoteId(self):
        f2 = makeContent(self.folder, 'f2', 'Folder')
        w1 = makeContent(f2, self.page1.id, self.wicked_type,
                         title='W1 Title')
        w2 = makeContent(f2, 'w2_id', self.wicked_type,
                         title='W2 Title')
        w2.setBody("((%s))" % self.page1.id)
        self.failUnlessWickedLink(w2, w1)
        self.failIfWickedLink(w2, self.page1)

    def testLocalTitleBeatsRemoteId(self):
        f2 = makeContent(self.folder, 'f2', 'Folder')
        w1 = makeContent(f2, 'w1_id', self.wicked_type,
                         title=self.page1.id)
        w2 = makeContent(f2, 'w2_id', self.wicked_type,
                         title='W2 Title')
        w2.setBody("((%s))" % self.page1.id)
        self.failUnlessWickedLink(w2, w1)
        self.failIfWickedLink(w2, self.page1)

    def testInexactLocalTitleNotBlockRemoteTitle(self):
        f2 = makeContent(self.folder, 'f2', 'Folder')
        w1 = makeContent(self.folder, 'w1', self.wicked_type,
                         title='W1 Title')
        w2 = makeContent(f2, 'w2', self.wicked_type,
                         title='%s With Extra' % w1.Title())
        w3 = makeContent(f2, 'w3', self.wicked_type,
                         title='W3 Title')
        w3.setBody("((%s))" % w1.Title())
        self.failUnlessWickedLink(w3, w1)
        self.failIfWickedLink(w3, w2)

    def testInexactLocalTitleNotBlockRemoteId(self):
        f2 = makeContent(self.folder, 'f2', 'Folder')
        w1 = makeContent(self.folder, 'w1', self.wicked_type,
                         title='W1 Title')
        w2 = makeContent(f2, 'w2', self.wicked_type,
                         title='%s With Extra' % w1.id)
        w3 = makeContent(f2, 'w3', self.wicked_type,
                         title='W3 Title')
        w3.setBody("((%s))" % w1.id)
        self.failUnlessWickedLink(w3, w1)
        self.failIfWickedLink(w3, w2)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDocCreation))
    suite.addTest(unittest.makeSuite(TestWikiLinking))
    suite.addTest(unittest.makeSuite(TestLinkNormalization))
    suite.addTest(unittest.makeSuite(TestRemoteLinking))
    return suite

if __name__ == '__main__':
    framework()
