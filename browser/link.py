from Products.Five import BrowserView
from Products.wicked.lib.utils import memoizedproperty
from interfaces import WickedLink

_marker=object()

class WickedLink(BrowserView):
    """
    renderer for wicked links
    """
    
    def __init__(self, context, request):
        self._context = (context,)
        self.request = request
        
    @property
    def context(self):
        return self._context[0]

    @memoizedproperty
    def howmany(self):
        return len(self.links)

    @property
    def multiple(self):
        return self.howmany > 1

    @memoizedproperty
    def links(self):
        return self._links

    @property
    def singlelink(self):
        return self.links[0]

    @clearmemo
    def load(self, links, chunk, section=_marker):
        self._links = links
        self.chunk = chunk
        if section is _marker:
            assert self.section
            return
        self.section = section
