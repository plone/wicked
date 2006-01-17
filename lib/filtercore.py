from zope.interface import implements
from normalize import titleToNormalizedId as normalize
from interfaces import IMacroCacheManager as IManageCaches

from utils import getRelativePath
PRINT = True

_marker = object()

def setup(filtercore):
    def setupwrapper(*args, **kwargs):
        wfilter, chunk = args
        kwargs = wfilter.configure(**kwargs)
        normalized = normalize(chunk)
        return filtercore(wfilter, chunk, normalized, **kwargs)
    return setupwrapper
    
def cache(filtercore, iface=IManageCaches):
    def cache(wfilter, chunk, normalized, *args, **kwargs):
        # cache depends on query and match
        # this could use some untangling
        # generic function?
        brain_flag = kwargs.get('return_brain', _marker)
        if brain_flag is _marker:
            cache = iface(wfilter)
            value = cache.get(normalized)
            if not value:
                vals = filtercore(wfilter, chunk, normalized, **kwargs)
                if not vals or not isinstance(vals, tuple):
                    return vals
                uid, value = vals
                if uid:
                    cache.set((normalized, uid), value)
                
            value = wfilter.localizeSlug(value)
            return value
        return filtercore(wfilter, chunk, normalized, **kwargs) 
    return cache

def query(filtercore):
    def querymatch(wfilter, chunk, normalized,  **kwargs):
        seeker = wfilter.getSeeker(chunk, normalized)
        brains = seeker.search()
        if not brains:
            brains = seeker.scopedSearch()
        return filtercore(wfilter, chunk, brains, **kwargs)
    return querymatch

# other utilty closures #

def onlybrain(setup):
    def onebrain(wfilter, chunk, **kwargs):
        kwargs.update(dict(return_brain=True))
        brain=setup(wfilter, chunk,  **kwargs)
        return brain
    return onebrain

def match(query):
    def match(self, best_match=True):
        data = query(self)
        if data and best_match:
            return [getMatch(self.chunk, data, normalled=self.normalled)]
        return data
    return match

# Filter utility methods #

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
    >>> from testing.general import portal_url, dummy, pdo
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
    return attrs and attrs

import doctest, unittest
def test_suite(): 
    return unittest.TestSuite((
        doctest.DocFileSuite('decorator_intro.txt'),
        doctest.DocFileSuite('filtercore.txt'),
        doctest.DocTestSuite('filtercore')
        ))

if __name__=="__main__":
    unittest.TextTestRunner().run(test_suite())


