##########################################################
#
# Licensed under the terms of the GNU Public License
# (see docs/LICENSE.GPL)
#
# Copyright (c) 2005:
#   - The Open Planning Project (http://www.openplans.org/)
#   - Whit Morriss <whit at www.openplans.org>
#   - and contributors
#
##########################################################
from Products.Five import BrowserView
from Products.wicked.lib.utils import memoize, memoizedproperty, \
     clearbefore, counter

from interfaces import WickedLink

_marker=object()

class BasicLink(object):
    """renderer for wicked links"""
    section = _marker
    counter=counter()
    
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @memoizedproperty
    def howmany(self):
        return len(self.links)

    @memoizedproperty
    def multiple(self):
        return self.howmany > 1

    @memoizedproperty
    def links(self):
        """
        calculates urls
        """
        for link in self._links:
            link['url'] = self.request.physicalPathToURL(link['path'], 0)
        return self._links

    @property
    def singlelink(self):
        return self.links[0]

    @property
    def count(self):
        return self.counter.next()

    @clearbefore
    def load(self, links, chunk):
        self._links = links
        self.chunk = chunk


class BasicFiveLink(BrowserView, BasicLink):
    """
    Five prepared link implementation
    """
    __init__=BasicLink.__init__

import unittest
from zope.testing import doctest
optionflags = doctest.REPORT_ONLY_FIRST_FAILURE | doctest.ELLIPSIS
def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('link.txt', optionflags=optionflags),
        ))

if __name__=="__main__":
    unittest.TextTestRunner().run(test_suite())
