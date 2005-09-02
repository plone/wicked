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
from Products.filter import api as fapi
from Products.AdvancedQuery import Eq, Generic

from normalize import titleToNormalizedId

pattern = sre.compile('\(\(([\w\W]+?)\)\)') # matches ((Some Text To link 123))

def mkLink(f):
    def wrapper(*args, **kw):
        chunk, brain, instance = args
        link_brain = f(*args, **kw)
        if link_brain:
            return {'path': link_brain.getPath(),
                    'icon': link_brain.getIcon,
                    'rel_path': getRelativePath(link_brain.getPath(), instance)}
    return wrapper

def getMatch(chunk, brains, instance):
    """
    Given a set of query results and the wicked link text, return
    the brain that represents the correct object to link to, or
    None
    
    Assumes that brains are already ordered oldest to newest, so
    the first absolute match is the one returned.  Matches on id
    take priority over matches on title
    
    XXX I rewrote to prioritize the normalized id,
    since priority should go to matches within the paradign
    this also flatten the need to do title length matching
    XXX Nice! DWM: did a little optimization
    
    Currently title matches comparisons are just testing for equal
    
    length; since the index lookup was for an exact phrase, equal
    length implies the same title, not a string in a larger title.
    
    XXX do we want to be more forgiving w/ extra whitespace in the
    title?
    """
    normalled_chunk = titleToNormalizedId(chunk)
    link_brain = None
    if len(brains) == 1 and \
           (brains[0].getId == normalled_chunk \
            or brains[0].getId == chunk \
            or titleToNormalizedId(brains[0].Title) == normalled_chunk):
        return brains[0]

    id_dict = dict([(brain.getId, brain) for brain in brains])
    for unk in normalled_chunk, chunk:
        if id_dict.has_key(unk):
            return id_dict[unk]

    brains = [brain for brain in brains if titleToNormalizedId(brain.Title) == normalled_chunk]
    return brains and brains[0] or None

getMatch = mkLink(getMatch)

def getRelativePath(path, instance):
    """
    Get path relative to portal
    """
    portal_path = getToolByName(instance,
                                'portal_url').getPortalPath().split('/')
    path = path.split('/')
    return '/'.join(path[len(portal_path):])

    
class WickedFilter(fapi.MacroSubstitutionFilter):
    """
    Filter for creating core wiki behavior 
    """

    name = 'Wicked Filter'
    pattern = pattern

    def _filterCore(self, instance, chunk, **kwargs):
        """
        Use the portal catalog to find a list of possible links.
        fiter by path, present by macro
        """

        catalog = getToolByName(instance, 'portal_catalog')
        path = instance.aq_inner.aq_parent.absolute_url_path()
        id = chunk
        title = '"%s"' % chunk

        query = Generic('path', {'query': path, 'depth': 1}) \
                & (Eq('id', id) | Eq('Title', title) | Eq('id', titleToNormalizedId(title)))
        
        brains = catalog.evalAdvancedQuery(query, ('created',))

        link_brain = None

        if not brains:
            if kwargs['scope']:
                scope = getattr(instance, kwargs['scope'])
                if callable(scope):
                    scope = scope()
                query = Generic('path', scope) \
                        & (Eq('id', id) | Eq('Title', title))
            else:
                query = Eq('id', id) | Eq('Title', title)
                brains = catalog.evalAdvancedQuery(query, ('created',))

        # XXX do we need to support 'links' as a sequence or should
        #     we change to a single 'link'
        # DWM: eventually ;)
        link = getMatch(chunk, brains, instance)
        kwargs['links'] = link and [link] or []
        kwargs['chunk'] = chunk
        macro = kwargs['wicked_macro']; del kwargs['wicked_macro']
        return self._macro_renderer(instance, macro, **kwargs)
    
fapi.registerFilter(WickedFilter())
