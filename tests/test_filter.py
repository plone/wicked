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

from Products.wicked.lib.filter import getMatch

import copy

class Brain(object):

    def __init__(self):
        self.update(**dict(getIcon='',
                           Title='',
                           getId='',
                           path=''
                         ))

    def update(self, **kw):
        self.__dict__.update(kw)

    def getPath(self):
        return self.path + '/' + self.getId

def mkbrains(howmany):
    brain = Brain()
    return [copy.copy(brain) for x in range(howmany)]

class TestFilter(WickedTestCase):
    wicked_type = 'IronicWiki'
    wicked_field = 'body'

    def afterSetUp(self):
        super(TestFilter, self).afterSetUp()

    def test_getMatch(self):
        brains = mkbrains(10)
        chunk = "Some Text"
        brain = brains[7]
        brain.update(Title="Pretty Title", path="/portal", getId='some-text')

        # first short circuit
        self.assertEqual(getMatch(chunk, [brain], self.page1), {'path': '/portal/some-text', 'rel_path': 'some-text', 'icon': ''})

        # second short circuit
        match = {'path': '/portal/some-text', 'rel_path': 'some-text', 'icon': ''}
        self.assertEqual(getMatch(chunk, brains, self.page1), match)
        chunk = "blah"
        brain.update(getId="blah")
        match.update(dict(path='/portal/blah', rel_path='blah'))
        self.assertEqual(getMatch(chunk, brains, self.page1), match)

        # final normalled title match
        chunk=brain.Title
        self.assertEqual(getMatch(chunk, brains, self.page1), match)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestFilter))
    return suite

if __name__ == '__main__':
    framework()
