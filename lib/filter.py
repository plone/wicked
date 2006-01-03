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
from Products.filter.utils import createContext, macro_render
from Products.wicked import utils, config
from interfaces import IWickedFilter, IWickedQuery, IMacroCacheManager
from zope.interface import implements

import filtercore as fc
import sre

_marker = object()

pattern = sre.compile(r'\(\(([\w\W]+?)\)\)') # matches ((Some Text To link 123))

def renderChunk(wfilter, chunk, brains, *args,  **kwargs):
    uid = ''
    brains = filter(None, brains)
    if brains:
        uid = brains[0].UID
        
    brains = [fc.packBrain(b, wfilter.context) for b in brains]
        
    kwargs['links'] = brains
    kwargs['chunk'] = chunk
        
    slug = super(WickedFilter,
                 wfilter)._filterCore(wfilter.wicked_macro,
                                      template=wfilter.template, **kwargs)
    if kwargs.get('cache', None):
        return uid, slug
    return uid, wfilter.localizeSlug(slug)

def localizeSlug(wfilter, slug):
    return slug.replace(wfilter.url_signifier, wfilter.getBaseURL())

class WickedFilter(filters.MacroSubstitutionFilter):
    """
    Filter for creating core wiki behavior 
    """
    implements(IWickedFilter)

    # identity
    query_iface = IWickedQuery
    name = config.FILTER_NAME
    pattern = pattern
    url_signifier = "&amp;&amp;base_url&amp;&amp;"

    _configure_exclude=dict(return_brain=True)

    # config attrs
    scope = _marker
    wicked_macro = _marker
    template = _marker
    fieldname = None

    # methods
    getMatch = staticmethod(fc.getMatch)
    render = lambda match: renderChunk
    renderChunk = renderChunk
    localizeSlug = localizeSlug
    configure = fc.configure
    
    @fc.setup
    @fc.cache(IMacroCacheManager)
    @fc.query
    @render
    def _filterCore(self, chunk, return_brain=False, normalized=None, **kwargs):
        """
        see utils.py for complete details on how wicked modifies
        the standard macro filter
        """
        pass

    def getSeeker(self, chunk, normalled):
        """
        @return query object
        """
        seeker = self.query_iface(self)
        seeker.configure(chunk, normalled, self.scope)
        return seeker

    def getBaseURL(self):
        base_url = getattr(self, 'base_url', getToolByName(self.context, 'portal_url')())
        self.base_url = base_url
        return base_url

    @fc.setup    
    @fc.query
    def getLinkTargetBrain(self, chunk, brains, **kwargs):
        """
        returns a brain of the object that would be the link target
        for the 'link_text' parameter in the context of the 'self.context'
        object
        """
        if brains:
            return brains.pop()
        return None
        

    def renderLinkForBrain(self, template, macro, chunk, brain, **kw):
        """
        XXX replace with chunk
        returns rendered wicked link that would resolve to the object related
        to the specified brain

        - template: template containing the wicked link macro

        - macro: name of the wicked link macro

        - chunk: text that is the content of the wicked link

        - self.context: object on which the link is being rendered

        - brain: object to which the link should resolve
        """
##         kw['links'] = [packBrain(brain, self.context)]
##         kw['chunk'] = chunk
##         econtext = createContext(self.context, **kw)
##         template = self.context.restrictedTraverse(path=template)
##         macro = template.macros[macro]
##         return macro_render(macro, self.context, econtext, **kw)
        # deprecated, use renderchunk instead
        uid, brain = self.renderChunk(chunk, [brain])
        return brain
    
if __name__=="__main__":
    from testing.filtercore import dummy, fakecacheiface, fakefilter
    import doctest
    doctest.testmod()
