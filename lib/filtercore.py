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

PRINT = True

from utils import getRelativePath

CACHE_ACTIVE= True

_marker = object()

import inspect
def prstack():
    for e in inspect.stack():
        if e:
            line = list(e[1:])
            line[3] = '\n'.join(line[3]).strip()
            print "%s line %s %s \n-- %s --" %tuple(line[:4])

def onlybrain(setup):
    def onebrain(wfilter, chunk, **kwargs):
        kwargs.update(dict(return_brain=True))
        brain=setup(wfilter, chunk,  **kwargs)
        return brain
    return onebrain

def setup(filtercore):
    """
    normalizes chunk, configures filter object.
    funky represents the filtercore

    >>> def funky(f, chunk, norm, **kwargs):
    ...     return chunk, norm, f.has
    >>> funky = setup(funky)
    >>> funky(fakefilter(), 'yo momma', **dict(has='got snakeskin teeth'))
    ('yo momma', 'yo-momma', 'got snakeskin teeth')
    """
    def setupwrapper(*args, **kwargs):
        wfilter, chunk = args
        kwargs = wfilter.configure(**kwargs)
        normalized = titleToNormalizedId(chunk)
        return filtercore(wfilter, chunk, normalized, **kwargs)
    return setupwrapper

class FilterCacheChecker(object):
    """
    A decorator for adding caching to the _filterCore

    >>> cache = FilterCacheChecker(True)
    >>> def funky(f, chunk, norm, **kwargs):
    ...     uid = norm
    ...     if kwargs.get('return_brain'):
    ...         return 'brains!'
    ...     return uid, norm
    >>> fcache = {'bl-ah':'blah.txt'}
    >>> decorate = cache(fakecacheiface(fcache))
    >>> cache = decorate(funky)
    >>> wfilter = fakefilter()
    >>> cache(wfilter, 'yo', 'momma so fat', return_brain=True)
    'brains!'
    
    A match should return rendered text
    >>> cache(wfilter, "hello darlin\'", 'hello-darlin')
    '<link cached>'

    lets decorate our original cache from setup
    and hit the cache with some normalled text

    >>> cache = setup(cache)
    >>> cache(wfilter, 'bl ah', **dict(hello=True))
    'blah.txt'
    """
    def __init__(self, active):
        self.active = active
        
    def __call__(self, IManageCaches):
        self.cache_iface = IManageCaches
        return self.cache
    
    def cache(self, filtercore):
        def cache(*args, **kwargs):
            # cache depends on query and match
            # this could use some untangling
            wfilter, chunk, normalized = args
            brain_flag = kwargs.get('return_brain', _marker)
            if self.active and brain_flag is _marker:
                cache = self.cache_iface(wfilter)
                value = cache.get(normalized)
                if not value:
                    vals = filtercore(wfilter, chunk, normalized, **kwargs)
                    if isinstance(vals, tuple):
                        uid, value = vals
                        cache.set((normalized, uid), value)
                        return wfilter.localizeSlug(value)
                    return filtercore(wfilter, chunk, normalized, **kwargs)
                
                return wfilter.localizeSlug(value)
            return filtercore(wfilter, chunk, normalized, **kwargs) # not sure this ever gets hit
        return cache
    
cache = FilterCacheChecker(CACHE_ACTIVE)

def query(filtercore):
    """
    Produces a method that returns either the brain or
    the uid and the rendered link for an unrendered link

    >>> def funky(f, chunk, norm, brains, **kwargs):
    ...     return brains
    >>> wfilter = fakefilter()
    >>> query = query(funky)

    Look for something not there
    >>> query(wfilter, 'dud', 'blah')

    Look for something that is there
    >>> query(wfilter, 'findme', 'blah')
    ['We are brains!']

    Look for something that is scoped
    >>> query(fakefilter(), 'scoped', 'blah')
    ['We are brains!']

    Test with prior decorators
    >>> cache = FilterCacheChecker(True)
    >>> fcache = {'bl-ah':'blah.txt'}
    >>> cache = cache(fakecacheiface(fcache))
    >>> query = setup(cache(query))
    >>> query(wfilter, 'Bab bam', **{})
    ['We are brains!']

    Will hit cache
    >>> query(wfilter, 'bl ah', **{})
    'blah.txt'

    will error without matching
    >>> 
    """
    def query(wfilter, chunk, normalized,  **kwargs):
        seeker = wfilter.getSeeker()
        brains = seeker.search(chunk, normalized)
        if not brains:
            brains = seeker.scopedSearch(kwargs.get('scope', None))



        return filtercore(wfilter, chunk, normalized, brains, **kwargs)
    return query


def match(method):
    """
    """
    def match(wfilter, chunk, normalized, brains, **kwargs):
        link, uid = None, None
        
        return_brain = kwargs.get('return_brain', None)
        if brains:
            uid, link = wfilter.getMatch(chunk, brains, \
                                         normalled=intern(normalized), \
                                         return_brain=return_brain)
        if not return_brain:
            return wfilter.renderChunk(chunk, link, uid, normalized, **kwargs)
        return link
    return match

def packBrain(brain, context):
    return {'path': brain.getPath(),
            'icon': brain.getIcon,
            'rel_path': getRelativePath(brain.getPath(), context)}
    
def linkresult(matcher):
    def newGetMatch(self, chunk, brains, **kw):
        retval = None, None
        link_brain = matcher(self, chunk, brains, **kw)
        return_brain = kw.get('return_brain', False)
        
        if link_brain:
            if return_brain:
                return link_brain.UID, link_brain
            return link_brain.UID, packBrain(link_brain, self.context)
        
        return None, None
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
    from testing.filtercore import dummy, fakecacheiface, fakefilter
    import doctest
    doctest.testmod()
