##########################################################
#
# Licensed under the terms of the GNU Public License
# (see docs/LICENSE.GPL)
#
# Copyright (c) 2005:
#   - The Open Planning Project (http://www.openplans.org/)
#   - Whit Morriss <whit@kalistra.com>
#   - Rob Miller <rob@kalistra.com> (RaFromBRC)
#   - and contributors
#
##########################################################
"""
CMF/AT centric basic wikish filter
"""
from Products.CMFCore.utils import getToolByName
from Products.filter import filter as filters
from Products.wicked import utils, config
from Products.wicked.lib import interfaces  
from Products.wicked.lib import utils
from Products.wicked.lib.utils import memoizedproperty, memoize
from interfaces import IWickedFilter, IWickedQuery
from zope.component import getMultiAdapter
from zope.interface import implements, Interface
from normalize import titleToNormalizedId as normalize

import sre

_marker = object()

pattern = sre.compile(r'\(\(([\w\W]+?)\)\)') # matches ((Some Text To link 123))

class WickedBase(filters.Filter):
    pattern = pattern

class WickedFilter(WickedBase):
    """
    Filter for creating core wiki behavior 
    """
    implements(IWickedFilter)

    # identity
    query_iface = IWickedQuery
    name = config.FILTER_NAME

    # XXX
    url_signifier = "&amp;&amp;base_url&amp;&amp;"

    _configure_exclude=dict(return_brain=True)

    # config attrs
    scope = _marker
    section = None

    # methods
    getMatch = staticmethod(utils.getMatch)
    configure = utils.configure
    
    def _filterCore(self, chunk, **kwargs):
        kwargs = self.configure(**kwargs)
        normalled = normalize(chunk)
        links=self.getLinks(chunk, normalled)
        self.renderer.load(links, chunk)
        return self.renderer()

    @utils.linkcache
    @utils. memoize
    def getLinks(self, chunk, normalled):
        self.resolver.configure(chunk, normalled, self.scope)
        brains = self.resolver.search
        if not brains:
            brains = self.resolver.scopedSearch
        links = [utils.packBrain(b) for b in brains if b]
        return links

    @memoizedproperty
    def resolver(self):
        """
        @return query object
        """
        return getMultiAdapter((self, self.context), self.query_iface)

    @memoizedproperty    
    def backlinker(self):
        return getMultiAdapter((self, self.context), interfaces.IBacklinkManager)

    def manageLink(self, obj, link):
        self.backlinker.manageLink(obj, link)
        
    def manageLinks(self, links):
        self.backlinker.manageLinks(links)
        
    @memoizedproperty
    def cache(self):
        cachemanager = interfaces.IContentCacheManager(self.context)
        cachemanager.setName(self.section)
        return cachemanager
    
    @memoizedproperty
    def renderer(self):
        renderer = getMultiAdapter((self.context, self.context.REQUEST), Interface, 'link_renderer')
        renderer.section = self.section
        return renderer.__of__(self.context)
    
if __name__=="__main__":
    from testing.filtercore import dummy, fakecacheiface, fakefilter
    import doctest
    doctest.testmod()
