"""
Functions for the composition of the wicked filter

_filteCore sequence order, each step is a decorator

1. check cache (return)
   component: In the wicked filter,
   the initial cache layer could also serve as a
   tag permanence layer that supercedes tag matching

2. query & match

   -- query 
      component: returns possible matches
                 
   -- match (return brain)
      function: choose single or multiple matches from set
      returned by query
      
3. render link (return)
   (dataobject|rendered object)
   Rendering is handled by macro filter
"""
from zope.interface import implements
from normalize import titleToNormalizedId as normalize

from utils import getRelativePath
PRINT = True
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

    >>> from testing.filtercore import dummy, fakecacheiface, fakefilter
    >>> def funky(f, chunk, norm, **kwargs):
    ...     return chunk, norm, f.has
    >>> funky = setup(funky)
    >>> funky(fakefilter(), 'yo momma', **dict(has='got snakeskin teeth'))
    ('yo momma', 'yo-momma', 'got snakeskin teeth')
    """
    def setupwrapper(*args, **kwargs):
        wfilter, chunk = args
        kwargs = wfilter.configure(**kwargs)
        normalized = normalize(chunk)
        return filtercore(wfilter, chunk, normalized, **kwargs)
    return setupwrapper


class FilterCacheChecker(object):
    """
    A decorator for adding caching to the _filterCore

    >>> from testing.filtercore import dummy, fakecacheiface, fakefilter
    >>> cache = FilterCacheChecker(True)
    >>> def funky(f, chunk, norm, **kwargs):
    ...     uid = norm
    ...     if kwargs.get('return_brain'):
    ...         return 'brains!'
    ...     return uid, '$$' + norm
    >>> fcache = {'bl-ah':'blah.txt'}
    >>> decorate = cache(fakecacheiface(fcache))
    >>> cache = decorate(funky)
    >>> wfilter = fakefilter()
    >>> cache(wfilter, 'yo', 'momma so fat', return_brain=True)
    'brains!'
    
    A set should return rendered text
    >>> cache(wfilter, "hello darlin\'", 'hello-darlin')
    'http://fakeurl/hello-darlin'

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
        def cache(wfilter, chunk, normalized, *args, **kwargs):
            # cache depends on query and match
            # this could use some untangling
            # generic function?
            brain_flag = kwargs.get('return_brain', _marker)
            if self.active and brain_flag is _marker:
                cache = self.cache_iface(wfilter)
                value = cache.get(normalized)
                if not value:
                    vals = filtercore(wfilter, chunk, normalized, **kwargs)
                    if not vals or not isinstance(vals, tuple):
                        return vals
                    uid, value = vals
                    if uid:
                        cache.set((normalized, uid), value)
                return wfilter.localizeSlug(value)
            return filtercore(wfilter, chunk, normalized, **kwargs) 
        return cache
    
cache = FilterCacheChecker(CACHE_ACTIVE)

def query(filtercore):
    """
    Produces a method that returns either the brain or
    the uid and the rendered link for an unrendered link

    >>> from testing.filtercore import dummy, fakecacheiface, fakefilter
    >>> def funky(f, chunk, brains, **kwargs):
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
    >>> query(wfilter, 'Bab bam')
    ['We are brains!']

    Will hit cache
    >>> query(wfilter, 'bl ah')
    'blah.txt'

    will error without matching
    >>> 
    """
    def querymatch(wfilter, chunk, normalized,  **kwargs):
        seeker = wfilter.getSeeker(chunk, normalized)
        brains = seeker.search()
        if not brains:
            brains = seeker.scopedSearch()
        return filtercore(wfilter, chunk, brains, **kwargs)
    return querymatch

## def match(method):
##     """
##     """
##     def match(wfilter, chunk, normalized, brains, **kwargs):
##         link, uid = None, None
##         return_brain = kwargs.get('return_brain', None)
##         if brains:
##             uid, link = wfilter.getMatch(chunk, brains, \
##                                          normalled=intern(normalized), \
##                                          return_brain=return_brain)
##         if not return_brain:
##             return wfilter.renderChunk(chunk, link, uid, normalized, **kwargs)
##         return link
##     return match

## def linkresult(matcher):
##     def newGetMatch(self, chunk, brains, **kw):
##         retval = None, None
##         link_brain = matcher(self, chunk, brains, **kw)
##         return_brain = kw.get('return_brain', False)
        
##         if link_brain:
##             if return_brain:
##                 return link_brain.UID, link_brain
##             return link_brain.UID, packBrain(link_brain, self.context)
        
##         return None, None
##     return newGetMatch

def packBrain(brain, context):
    """
    converts dataobjects in to template ready dictionaries
    
    >>> from testing.general import portal_url, dummy, pdo
    >>> pu = portal_url()
    >>> context = dummy(dict(portal_url=pu))
    >>> brain = pdo(getId='somepage', getIcon='someicon')
    >>> link = packBrain(brain, context)
    >>> link['path'] == '%s/%s' %(pu.getPortalPath(), brain.getId)
    True
    
    >>> link['icon'] == brain.getIcon
    True
    
    >>> link['rel_path'] == brain.getId
    True
    """
    return {'path': brain.getPath(),
            'icon': brain.getIcon,
            'rel_path': getRelativePath(brain.getPath(), context)}

def getMatch(chunk, brains, normalled=None):
    """
    Given a set of query results and the wicked link text, return
    the brain that represents the correct object to link to, or
    None
    
    Assumes that brains are already ordered oldest to newest, so
    the first absolute match is the one returned.  Matches on id
    take priority over matches on title

    all strings are normalized and interned for comparison matches.

    >>> from testing.general import pdo
    >>> mkbrain = lambda i: pdo(getId='-'.join([str(x) for x in i]), Title='%s %s' %i, created=i[1])
    >>> seed = zip('abc', range(3))
    >>> brains = [mkbrain(i) for i in seed]
    >>> chunk = ''
    >>> normalled = ''

    Test null conditions

    >>> getMatch(chunk, brains)
    >>> getMatch(chunk, brains, normalled)
    >>> getMatch(chunk, brains[:1], normalled)

    Test single brain matches

    >>> getMatch('', brains[:1], 'a-0').getId
    'a-0'
    
    >>> getMatch(brains[0].getId, brains[:1], 'blah').getId
    'a-0'

    >>> getMatch(brains[0].Title, brains[:1]).getId
    'a-0'

    Test multi brain matches. brain 0 should win over brain 3
    for all matches

    >>> from copy import copy
    >>> newbrain = copy(brains[0])
    >>> newbrain.update(dict(created=3))
    >>> brains =   brains + [newbrain]
    >>> getMatch('', brains, 'a-0').created
    0
    
    >>> getMatch(brains[0].getId, brains).created
    0

    >>> getMatch(brains[0].Title, brains).created
    0

    Test title to chunk match

    >>> brains[3].Title='A unique title'
    >>> getMatch(brains[3].Title, brains).Title
    'A unique title'

    """
    normalled_chunk = normalled
    if not normalled_chunk:
        normalled_chunk = intern(normalize(chunk))
    link_brain = None
    if len(brains) == 1 and \
           (intern(brains[0].getId) is normalled_chunk \
            or intern(brains[0].getId.strip()) is intern(chunk.strip()) \
            or intern(normalize(brains[0].Title)) is normalled_chunk):
        return brains[0]

    # trick...
    # reversing the brains clobbers
    # older matches with the same id

    btup = [(brain.getId, brain) for brain in brains]
    id_dict = dict(reversed(btup))
    for unk in normalled_chunk, chunk,:
        if id_dict.has_key(unk):
            return id_dict[unk]

    brains = [brain for brain in brains \
              if intern(normalize(brain.Title)) is normalled_chunk]
    return brains and brains[0] or None

def configure(self, **attrs):
    """
    For runtime configuration of filter.
    
    @param attrs: dict of 0-N key value pairs that
    will be set on the filter for the duration of
    its existence
    
    >>> from testing.general import dummy
    >>> troll = dummy(dict(_configure_exclude=dict(fo=True)))
    >>> configure(troll, **dict(fi='fie', fo='fum'))
    {'fo': 'fum'}
    
    >>> getattr(troll, 'fi', 'No fie?!!')
    'fie'
    
    When no term are exclude, configure should
    set and remove all kwargs passed in
    
    >>> configure(troll, **dict(englishman='yum'))
    {}
    
    >>> getattr(troll, 'englishman')
    'yum'
    
    Make sure a dict gets returned even if
    kwargs are empty
    
    >>> configure(troll, **dict())
    {}
    """
    [(setattr(self, key, attrs[key]), attrs.__delitem__(key)) \
     for key in attrs.keys() \
     if not self._configure_exclude.has_key(key)]
    return attrs and attrs or {}

if __name__=="__main__":
    import doctest
    doctest.testmod()
