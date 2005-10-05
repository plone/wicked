import os, sys, time
import unittest
from sets import Set
import traceback

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase

from Products.CMFCore.utils import getToolByName
from Products.filter import api as fapi
from Products.wicked.lib.filter import WickedFilter
from wickedtestcase import WickedTestCase

class TestWickedFilter(WickedTestCase):
    wicked_type = 'IronicWiki'
    wicked_field = 'body'

    def afterSetUp(self):
        """
        sets the body of page1 to be a wicked link of the id of page2
        """
        WickedTestCase.afterSetUp(self)
        field = self.page1.getField(self.wicked_field)
        field.getMutator(self.page1)("((%s))" % self.page2.getId())
        self.wkd_filter = fapi.getFilter(WickedFilter.name)

    def test_getLinkTargetBrain(self):
        brain = self.wkd_filter.getLinkTargetBrain(self.page1,
                                                   self.page2.getId())
        self.failUnless(brain.getObject()) == self.page2

    def test_renderLinkForBrain(self):
        cat = getToolByName(self.portal, 'portal_catalog')
        brain = cat(id=self.page2.getId())[0]
        field = self.page1.getField(self.wicked_field)

        rendered = self.wkd_filter.renderLinkForBrain(field.template,
                                                      field.wicked_macro,
                                                      brain.id,
                                                      self.page1,
                                                      brain)
        self.failUnless(rendered in field.getAccessor(self.page1)())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestWickedFilter))
    return suite

if __name__ == '__main__':
    framework()
