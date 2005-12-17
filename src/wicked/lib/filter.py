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

import sre
from Products.CMFCore.utils import getToolByName
from Products.filter.utils import createContext, macro_render

from wicked import utils, config
from Products.filter import filter as filters
from normalize import titleToNormalizedId
from zope.interface import implements
from interfaces import IWickedFilter, IWickedQuery

_marker = object()

pattern = sre.compile(r'\(\(([\w\W]+?)\)\)') # matches ((Some Text To link 123))

from utils import getMatch, delsetif, cache, query

class WickedFilter(filters.MacroSubstitutionFilter):
    """
    Filter for creating core wiki behavior 
    """
    implements(IWickedFilter)

    name = config.FILTER_NAME
    pattern = pattern
    getMatch = getMatch
    delkw = staticmethod(delsetif)

    wicked_macro = _marker
    template = _marker
    fieldname = None

    @cache
    @query
    def _filterCore(self, chunk, return_brain=False, normalized=None, **kwargs):
        """
        see utils.py for complete details on how wicked modifies
        the standard macro filter
        """

        # these allow filter core to run without the decorator
        # but are redundant
        # if not normalized:
        #    normalized = titleToNormalizedId(chunk)

        # these should not change 
        # for the life of the instance
        
        fattrs = 'wicked_macro', 'template',
        [self.delkw(self, attr, kwargs, _marker) \
         for attr in fattrs]

        # these must remain more dynamic
        kwargs['chunk'] = chunk
        
        return super(WickedFilter,
                     self)._filterCore(self.wicked_macro,
                                       template=self.template, **kwargs)

    def getLinkTargetBrain(self, link_text, **kwargs):
        """
        returns a brain of the object that would be the link target
        for the 'link_text' parameter in the context of the 'self.context'
        object
        """
        return self._filterCore(link_text, return_brain=True,
                                **kwargs)

    def renderLinkForBrain(self, template, macro, text, brain, **kw):
        """
        returns rendered wicked link that would resolve to the object related
        to the specified brain

        - template: template containing the wicked link macro

        - macro: name of the wicked link macro

        - text: text that is the content of the wicked link

        - self.context: object on which the link is being rendered

        - brain: object to which the link should resolve
        """
        kw['links'] = [{'path': brain.getPath(),
                        'icon': brain.getIcon,
                        'rel_path': utils.getPathRelToPortal(brain.getPath(),
                                                       self.context)}]
        kw['chunk'] = text
        econtext = createContext(self.context, **kw)
        template = self.context.restrictedTraverse(path=template)
        macro = template.macros[macro]
        return macro_render(macro, self.context, econtext, **kw)
