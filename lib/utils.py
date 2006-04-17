from normalize import titleToNormalizedId as normalize

def linkcache(func):
    def cache(wfilter, chunk, normalized):
        # cache depends on query and match
        # this could use some untangling
        # generic function? 
        value = wfilter.cache.get(normalized)
        if not value:
            value = func(wfilter, chunk, normalized)
            if value:
                uid = value[0]['uid']
                wfilter.cache.set((normalized, uid), value)
        return value
    return cache

def match(query):
    def match(self, best_match=True):
        data = query(self)
        if data and best_match:
            return [getMatch(self.chunk, data, normalled=self.normalled)]
        return data
    return match

def packBrain(brain):
    """
    converts dataobjects in to template ready dictionaries
    """
    return dict(path=brain.getPath(),
                icon=brain.getIcon,
                uid=brain.UID,
                rid=brain.data_record_id_)

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
        normalled_chunk = normalize(chunk)
    normalled_chunk = intern(normalled_chunk)
    
    link_brain = None
    if len(brains) == 1 and \
           (intern(brains[0].getId) is normalled_chunk \
            or intern(brains[0].getId.strip()) is intern(chunk.strip()) \
            or intern(normalize(brains[0].Title)) is normalled_chunk):
        return brains[0]

    # first, match id

    # reversing the brains into a dict clobbers younger matches with
    # the same id. we'll match against the normalled chunk, then the
    # chunk (for single work chunks)

    btup = [(brain.getId, brain) for brain in brains]
    id_dict = dict(reversed(btup))
    for unk in normalled_chunk, chunk,:
        if id_dict.has_key(unk):
            return id_dict[unk]

    # second, match Title
    
    brains=[brain for brain in brains \
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







def removeParens(wikilink):
    wikilink.replace('((', '')
    wikilink.replace('))', '')
    return wikilink


def counter():
    count=0
    while True:
        count+=1
        yield count

_marker = object()
class Memoizer(object):
    propname = '_mp_cache'
    def clearbefore(self, func):
        def clear(*args, **kwargs):
            inst=args[0]
            if hasattr(inst, self.propname):
                delattr(inst, self.propname)
            return func(*args, **kwargs)
        return clear

    def memoizedproperty(self, func):
        return property(self.memoize(func))

    def memoize(self, func):
        def memogetter(*args, **kwargs):
            inst = args[0]
            cache = getattr(inst, self.propname, dict())
            key=hash((func.__name__, args, frozenset(kwargs)))
            val = cache.get(key, _marker)
            if val is _marker:
                val=func(*args, **kwargs)
                cache[key]=val
                setattr(inst, self.propname, cache)
            return val
        return memogetter

_m = Memoizer()
memoize = _m.memoize
memoizedproperty = _m.memoizedproperty
clearbefore = _m.clearbefore
    
import unittest
from zope.testing import doctest
optionflags = doctest.REPORT_ONLY_FIRST_FAILURE | doctest.ELLIPSIS
def test_suite():

    return unittest.TestSuite((
        doctest.DocFileSuite('decorator_intro.txt', optionflags=optionflags),
        #doctest.DocFileSuite('filtercore.txt', optionflags=optionflags),
        doctest.DocTestSuite('utils', optionflags=optionflags)
        ))

if __name__=="__main__":
    unittest.TextTestRunner().run(test_suite())

