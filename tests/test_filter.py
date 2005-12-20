import os, sys, time
import unittest
from sets import Set
import traceback

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase

from Products.CMFCore.utils import getToolByName
from Products.filter import api as fapi
from Products.wicked import utils
from Products.wicked.lib.filter import WickedFilter
from wickedtestcase import WickedTestCase
from Products.filter.interfaces import IFieldFilter

class TestWickedFilter(WickedTestCase):
    wicked_type = 'IronicWiki'
    wicked_field = 'body'

    def afterSetUp(self):
        """
        sets the body of page1 to be a wicked link of the id of page2
        """
        super(TestWickedFilter, self).afterSetUp()
        field = self.page1.getField(self.wicked_field)
        self.text = text = "((%s))" % self.page2.getId()
        field.getMutator(self.page1)(text)
        self.filter = utils.getFilter(self.page1)
        self.field = field

    def test_getLinkTargetBrain(self):
        brain = self.filter.getLinkTargetBrain(self.page2.getId())
        self.failUnless(brain.getObject()) == self.page2

    def test_renderChunk(self):
        cat = getToolByName(self.portal, 'portal_catalog')
        brain = cat(id=self.page2.getId())[0]
        field = self.page1.getField(self.wicked_field)

        self.filter.configure(**dict(template=field.template, wicked_macro=field.wicked_macro))
        uid, rendered = self.filter.renderChunk(brain.getId, brain)
        self.failUnless(rendered in field.getAccessor(self.page1)())

##     def test_decoratorchaining(self):
##         field = self.field
##         config = dict(scope=field.scope,
##                       fieldname=field.getName(),
##                       wicked_macro=field.wicked_macro,
##                       template=field.template)
##         wfilter = self.filter
##         callfc = lambda chunk, kwargs: wfilter._filtercore(chunk, **kwargs)
##         callfc(, **config)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestWickedFilter))
    return suite

if __name__ == '__main__':
    framework()
