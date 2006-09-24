import os, sys, time
import unittest
from sets import Set
import traceback

from Testing import ZopeTestCase
from wickedtestcase import WickedTestCase, makeContent
from Products.wicked.lib.normalize import titleToNormalizedId
from Products.wicked.config import BACKLINK_RELATIONSHIP

stx_body = """
Here is some structured text data:

- with

- a

- bulleted

- list
"""

class TestWickedRendering(WickedTestCase):
    wicked_type = 'IronicWiki'
    wicked_field = 'body'
    
    def test_stxRendering(self):
        self.page1.setBody(stx_body, mimetype='text/structured')
        self.failUnless('<ul>' in self.page1.getBody())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestWickedRendering))
    return suite

