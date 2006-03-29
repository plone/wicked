from Products.Five import BrowserView
from Products.wicked.lib.utils import memoize, memoizedproperty, clearbefore, counter

from interfaces import WickedLink

_marker=object()

class BasicLink(object):
    """renderer for wicked links"""
    section = _marker
    counter=counter()
    
    def __init__(self, context, request):
        self._context = (context,)
        self.request = request
        
    @property
    def context(self):
        return self._context[0]

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
    def load(self, links, chunk, section=_marker):
        self._links = links
        self.chunk = chunk
        assert section is not _marker, 'Must supply a section name'
        self.section = section


class BasicFiveLink(BrowserView, BasicLink):
    """
    Five prepared link implementation
    """

import unittest
from zope.testing import doctest
optionflags = doctest.REPORT_ONLY_FIRST_FAILURE | doctest.ELLIPSIS
def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('link.txt', optionflags=optionflags),
        ))

if __name__=="__main__":
    unittest.TextTestRunner().run(test_suite())
