import os, sys, time
import unittest
from sets import Set
import traceback

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase

from Products.CMFCore.utils import getToolByName
from Products.Archetypes.utils import shasattr
from Products.filter import api as fapi
from Products.wicked import utils
from Products.filter.interfaces import IFieldFilter
from wickedtestcase import WickedTestCase
from Products.wicked.lib.interfaces import IWickedFilter, IMacroCacheManager

MARKER = 'marker'

class TestLinkCache(WickedTestCase):
    wicked_type = 'IronicWiki'
    wicked_field = 'body'

    def afterSetUp(self):
        """
        sets the body of page1 to be a wicked link of the id of page2
        """
        super(TestLinkCache, self).afterSetUp()
        field = self.page1.getField(self.wicked_field)

        field.getMutator(self.page1)("((%s))" % self.page2.Title())
        self.field = field
        self.filter = utils.getFilter(self.page1)
        self.filter.configure(**dict(fieldname=field.getName(),
                                     template=field.template,
                                     wicked_macro=field.wicked_macro))
        self.wicked_ccm = IMacroCacheManager(self.filter)
        
    def test_linkGetsCached(self):
        field = self.field
        wicked_ccm = self.wicked_ccm
        pg2_id = self.page2.getId()
        self.failUnless(wicked_ccm.get(pg2_id))

        cat = getToolByName(self.portal, 'portal_catalog')
        brain = cat(id=pg2_id)[0]
        uid, rendered = self.filter.renderChunk(self.page2.Title(), brain, cache=True)
        self.failUnlessEqual(self.strip(wicked_ccm.get(pg2_id)), self.strip(rendered))

    def test_cacheIsUsed(self):
        field = self.field
        wicked_ccm = self.wicked_ccm
        pg2_id = self.page2.getId()
        wicked_ccm.set((pg2_id, self.page2.UID()), MARKER)
        value = self.getRenderedWickedField(self.page1)
        self.failUnless(MARKER in value)
        self.failIfWickedLink(self.page1, self.page2)
        

def test_suite():
    suite = unittest.TestSuite()
    from Testing.ZopeTestCase import ZopeDocTestSuite
    suite.addTest(unittest.makeSuite(TestLinkCache))
    return suite

if __name__ == '__main__':
    framework()
