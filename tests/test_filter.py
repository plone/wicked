import os, sys, time
import unittest
from sets import Set
import traceback

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase

from Products.filter import api as fapi
from Products.wicked.lib.filter import WickedFilter
from wickedtestcase import WickedTestCase

class TestWickedFilter(WickedTestCase):
    wicked_type = 'IronicWiki'
    wicked_field = 'body'

    def test_getLinkTargetBrain(self):
        field = self.page1.getField(self.wicked_field)
        field.getMutator(self.page1)(self.page2.getId())
        wkd_filter = fapi.getFilter(WickedFilter.name)
        brain = wkd_filter.getLinkTargetBrain(self.page1,
                                              self.page2.getId())
        self.failUnless(brain.getObject()) == self.page2

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestWickedFilter))
    return suite

if __name__ == '__main__':
    framework()
