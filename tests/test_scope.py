import os, sys, time
import unittest
from sets import Set
import traceback

from Testing import ZopeTestCase

from Products.wicked.lib.normalize import titleToNormalizedId
from Products.wicked.config import BACKLINK_RELATIONSHIP
from Products.wicked.example import IronicWiki
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
    wicked_type = 'IronicWiki'
    wicked_field = 'body'

    def afterSetUp(self):
        WickedTestCase.afterSetUp(self)
        IronicWiki.scopeTester = scopeTester
        IronicWiki.schema['body'].scope = 'scopeTester'

    def beforeTearDown(self):
        del IronicWiki.scopeTester
        IronicWiki.schema['body'].scope = ''

    def test_insideScope(self):
        f2 = makeContent(self.folder, 'f2', 'Folder')
        w1 = makeContent(f2, 'w1', 'IronicWiki',
                          title='W1 Title')
        w1.setBody("((%s))" % self.page1.Title())
        self.failUnlessWickedLink(w1, self.page1)

    def test_outsideScope(self):
        f2 = makeContent(self.folder, 'f2', 'Folder')
        f3 = makeContent(f2, 'f3', 'Folder')
        w1 = makeContent(f3, 'w1', 'IronicWiki',
                          title='W1 Title')
        w1.setBody("((%s))" % self.page1.Title())
        self.failIfWickedLink(w1, self.page1)
        

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestWickedScope))
    return suite
