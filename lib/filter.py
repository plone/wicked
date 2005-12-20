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


from Products.CMFCore.utils import getToolByName
from Products.filter import filter as filters
from Products.filter.utils import createContext, macro_render
from Products.wicked import utils, config
from interfaces import IWickedFilter, IWickedQuery, IMacroCacheManager
from normalize import titleToNormalizedId
from zope.interface import implements
import sre

_marker = object()

pattern = sre.compile(r'\(\(([\w\W]+?)\)\)') # matches ((Some Text To link 123))

from filtercore import getMatch, setup, cache, \
     query, match, packBrain, onlybrain, \
     prstack
from utils import delsetif





def renderChunk(wfilter, chunk, brain, *args,  **kwargs):
    if brain and not isinstance(brain, dict):
        brain=packBrain(brain, wfilter.context)
        
    kwargs['links'] = brain and [brain] or []
    kwargs['chunk'] = chunk
        
    uid = args and args[0] or None
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

    # identity
    implements(IWickedFilter)
    query_iface = IWickedQuery
    name = config.FILTER_NAME
    pattern = pattern
    url_signifier = "&amp;&amp;base_url&amp;&amp;"

    # config attrs
    wicked_macro = _marker
    template = _marker
    fieldname = None

    # methods
    getMatch = getMatch
    delkw = staticmethod(delsetif)
    render = lambda match: renderChunk
    renderChunk = renderChunk
    localizeSlug = localizeSlug

    @setup
    @cache(IMacroCacheManager)
    @query
    @match
    @render
    def _filterCore(self, chunk, return_brain=False, normalized=None, **kwargs):
        """
        see utils.py for complete details on how wicked modifies
        the standard macro filter
        """
        if __debug__:
            prstack()
        pass

    def getSeeker(self):
        """
        @return query object
        """
        return self.query_iface(self)

    def getBaseURL(self):
        base_url = getattr(self, 'base_url', getToolByName(self.context, 'portal_url')())
        self.base_url = base_url
        return base_url

    def configure(self, **attrs):
        """
        For runtime configuration of filter.  with at, most
        of configuration data is from the field
        """
        # make smarter / safer
        [(setattr(self, key, attrs[key]), attrs.__delitem__(key)) \
         for key in attrs.keys() if key != 'return_brain']
        return attrs

    @onlybrain    
    @setup    
    @query
    @match
    def getLinkTargetBrain(self, link_text, *args, **kwargs):
        """
        returns a brain of the object that would be the link target
        for the 'link_text' parameter in the context of the 'self.context'
        object
        """
        if __debug__:
            prstack()
        pass

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
        uid, brain = self.renderChunk(chunk, brain)
        return brain
