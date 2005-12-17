"""
Functions for the composition of the wicked filter

_filteCore sequence order

1. check cache (return)
   decorator + component: In the wicked filter,
   the initial cache layer could also serve as a
   tag permanence layer that supercedes tag matching
2. query (continue)
   component: could plug into other query mechanisms
              for extension
3. match (return brain)
   function: match is simply a logical algorithm
4. render link (return)
   (dataobject|rendered object)
   Rendering is handled by macro filter
"""

from zope.interface import implements
from normalize import titleToNormalizedId
try:
    from Products.CMFCore.utils import getToolByName
except ImportError:
    pass

_marker = object()

from interfaces import IMacroCacheManager
from normalize import titleToNormalizedId
from interfaces import IWickedQuery, IMacroCacheManager

CACHE_ACTIVE= True

_marker = object()

class FilterCacheChecker(object):
    """
    A decorator for adding caching to the _filterCore
    """
    def __init__(self, active):
        self.active = active
        
    def __call__(self, filtercore):
        """
        generic function? bueller?
        """
        def cache(*args, **kwargs):
            inst, chunk = args
            normalized = titleToNormalizedId(chunk)

            # ugly AT necessity, though other system may need
            # a sort of field distinction also
            inst.fieldname = kwargs.get('fieldname', False)

            brain = kwargs.get('return_brain', _marker)
            if not brain is _marker and self.active:
                manager = IMacroCacheManager(inst)
                value = manager.get(normalized)
                if not value: 
                    value = filtercore(inst, chunk, normalized=normalized, **kwargs)
                    return manager.set(normalized, value)
            return filtercore(inst, chunk, normalized=normalized, **kwargs)
        return cache

cache = FilterCacheChecker(CACHE_ACTIVE)

def query(filtercore):
    def queryprep(inst, chunk, normalized=None, **kwargs):
        seeker = IWickedQuery(inst)
        brains = seeker.search(chunk, normalized)
        if not brains:
            brains = seeker.searchWide(kwargs.get('scope', None))

        link = None
        return_brain = kwargs.get('return_brain', None)
        
        if brains:
            link = inst.getMatch(chunk, brains, \
                                 normalled=intern(normalized), return_brain=return_brain)

        if return_brain: return link
        
        kwargs['links'] = link and [link] or []

        return filtercore(inst, chunk, normalized=normalized, **kwargs)
    return queryprep

def delsetif(obj, attr, argdict, marker):
    """
    remove a value from a dict and set it on an
    object if it is currently unset or the marker

    >>> _marker = object()
    >>> inst = type('dummy', (object,), {})()
    >>> inst.dog = _marker
    >>> inst.dog is _marker
    True
    >>> kw = dict(bob=1, dog=2)
    >>> [delsetif(inst, key, kw, _marker) for key in kw.keys()]
    [None, None]
    >>> inst.dog
    2
    >>> inst.bob
    1
    >>> kw
    {}
    """
    value = argdict.pop(attr)
    if getattr(obj, attr, marker) is marker:
        setattr(obj, attr, value)
    
def getRelativePath(path, instance):
    """
    Get path relative to portal
    """
    portal_path = getToolByName(instance,
                                'portal_url').getPortalPath().split('/')
    path = path.split('/')
    return '/'.join(path[len(portal_path):])

def linkresult(matcher):
    def newGetMatch(self, chunk, brains, **kw):
        link_brain = matcher(self, chunk, brains, **kw)
        return_brain = kw.get('return_brain', False)
        if return_brain:
            return link_brain

        if link_brain:
            return {'path': link_brain.getPath(),
                    'icon': link_brain.getIcon,
                    'rel_path': getRelativePath(link_brain.getPath(), self.context)}
        return None
    return newGetMatch

@linkresult
def getMatch(self, chunk, brains, normalled=None, **kw):
    """
    Given a set of query results and the wicked link text, return
    the brain that represents the correct object to link to, or
    None
    
    Assumes that brains are already ordered oldest to newest, so
    the first absolute match is the one returned.  Matches on id
    take priority over matches on title

    all strings are normalized and interned for comparison matches.
    """
    normalled_chunk = normalled
    if not normalled_chunk:
        normalled_chunk = intern(titleToNormalizedId(chunk))
    link_brain = None
    if len(brains) == 1 and \
           (intern(brains[0].getId) is normalled_chunk \
            or intern(brains[0].getId.strip()) is intern(chunk.strip()) \
            or intern(titleToNormalizedId(brains[0].Title)) is normalled_chunk):
        return brains[0]

    # trick...
    # reversing the brains clobbers
    # older matches with the same id

    btup = [(brain.getId, brain) for brain in brains]
    id_dict = dict(reversed(btup))
    for unk in normalled_chunk, chunk:
        if id_dict.has_key(unk):
            return id_dict[unk]

    brains = [brain for brain in brains if intern(titleToNormalizedId(brain.Title)) is normalled_chunk]
    return brains and brains[0] or None

if __name__=="__main__":
    import doctest
    doctest.testmod()
