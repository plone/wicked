"""
Functions for the composition of the wicked filter

_filteCore sequence order

1. check cache (return)
2. query (continue)
3. match (return brain)
4. render link (return)

1. component: In the wicked filter, the initial cache step could also serve as a
tag permanence layer that supercedes tag matching

2. component: could plug into other query mechanisms for extension

4. component: match is simply a logical algorithm

5. return (dataobject|rendered object)
"""

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

def prep(filtercore):
    def prepmacro(inst, chunk, normalized=None, **kwargs):
        # these should not change 
        # for the life of the instance
        # remove and conditionally set
        
        fattrs = 'wicked_macro', 'template',
        [inst.delkw(inst, attr, kwargs, _marker) \
         for attr in fattrs]

        # these must remain more dynamic

        #kwargs['chunk'] = chunk
        return filtercore(inst, chunk, normalized=normalized, **kwargs)
    return prepmacro
