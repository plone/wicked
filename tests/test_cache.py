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
from Products.wicked.lib.filter import WickedFilter
from wickedtestcase import WickedTestCase

MARKER = 'marker'

class TestLinkCache(WickedTestCase):
    wicked_type = 'IronicWiki'
    wicked_field = 'body'

    def afterSetUp(self):
        """
        sets the body of page1 to be a wicked link of the id of page2
        """
        WickedTestCase.afterSetUp(self)
        field = self.page1.getField(self.wicked_field)
        field.getMutator(self.page1)("((%s))" % self.page2.getId())
        self.field = field
        self.filter = fapi.getFilter(WickedFilter.name)

    def test_linkGetsCached(self):
        field = self.field
        wicked_cache = self.page1._wicked_cache
        cached_links = wicked_cache[field.getName()]
        pg2_id = self.page2.getId()
        self.failUnless(cached_links.has_key(pg2_id))

        cat = getToolByName(self.portal, 'portal_catalog')
        brain = cat(id=pg2_id)[0]
        rendered = self.filter.renderLinkForBrain(field.template,
                                                  field.wicked_macro,
                                                  pg2_id,
                                                  self.page1,
                                                  brain)
        self.failUnless(cached_links[pg2_id] == rendered)

    def test_cacheIsUsed(self):
        field = self.field
        wicked_cache = self.page1._wicked_cache
        cached_links = wicked_cache[field.getName()]
        pg2_id = self.page2.getId()
        cached_links[pg2_id] = MARKER
        value = self.getRenderedWickedField(self.page1)
        self.failUnless(MARKER in value)
        self.failIf(self.hasWickedLink(self.page1, self.page2))
        

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestLinkCache))
    return suite

if __name__ == '__main__':
    framework()
