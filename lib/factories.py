from zope.interface import implements
try:
    from Products.CMFCore.utils import getToolByName
    from Products.AdvancedQuery import Eq, Generic
except ImportError:
    pass

from interfaces import IContentCacheManager, IWickedQuery
from normalize import titleToNormalizedId

class WickedCatalogInquisitor(object):
    """
    CMFish catalog query handler
    """
    implements(IWickedQuery)
    
    def __init__(self, context):
        self.context = context # the filter
        content = self.content = self.context.context
        self.catalog = getToolByName(content, 'portal_catalog')
        self.path = '/'.join(content.aq_inner.aq_parent.getPhysicalPath())    
        self.evalQ = self.catalog.evalAdvancedQuery

    def searchWide(self, scope):
        chunk, title = self.chunk, self.title
        query = (Eq('getId', chunk) | Eq('Title', title))
        if scope:
            scope = getattr(self.content, scope)
            if callable(scope):
                scope = scope()
            query = Generic('path', scope) & query
        return self.evalQ(query, ('created',))

    def search(self,  chunk, normalized):
        self.chunk = chunk
        getId = chunk
        self.title = title = '"%s"' % chunk
        query = Generic('path', {'query': self.path, 'depth': 1}) \
                & (Eq('getId', chunk) | Eq('Title', title) | Eq('getId', normalized))

        return self.evalQ(query, ('created',))


class ContentCacheManager(object):
    """
    basic manager for quick and dirty caching links
    on a content object.

    First, fake some AT content and a filter
    
    >>> content = type('dummy', (object,), {})()
    >>> content.aq_base = content
    >>> from testing import Filter
    >>> fil = Filter(content)
    >>> fil.fieldname = 'body'

    Lets manage that hot content cache!
    
    >>> ccm=ContentCacheManager(fil)
    >>> ccm.context == fil
    True
    >>> ccm.content == content
    True
    >>> ccm.get('bob')

    >>> ccm.set('dog', 'some dog text')
    'some dog text'
    >>> ccm.set('bob', 'some text')
    'some text'
    >>> ccm.get('bob')
    'some text'
    >>> getattr(content, ccm.cache_attr)
    {'body': {'bob': 'some text', 'dog': 'some dog text'}}
    
    >>> ccm.unset('bob')
    'some text'
    >>> _marker = object()
    >>> ccm.get('bob', _marker) is _marker
    True
    >>> ccm.get('dog')
    'some dog text'
    >>> ccm.get('billybob')

    """
    implements(IContentCacheManager)
    cache_attr = '_wicked_cache'

    def __init__(self, context):
        self.context = context # the filter
        self.content = context.context # the parent object
        self.name = self.context.fieldname

    def _getStore(self):
        args = (self.content.aq_base, self.cache_attr)
        if not hasattr(*args):
            setattr(*args + (dict(),))
        return getattr(*args)

    def _getCache(self):
        store = self._getStore()
        cache = store.get(self.name, {})
        if cache:
            return cache
        store[self.name] = cache
        return cache
    
    def get(self, key, default=None):
        """
        >>> content, ccm = testsetup()
        >>> key = 'bob'
        >>> ccm.get(key)

        >>> _marker = object()
        >>> ccm.get(key, _marker) is _marker
        True
        >>> ccm.content._wicked_cache['body'][key] = 'some text'
        >>> ccm.get(key)
        'some text'
        """
        cache = self._getCache()
        if cache.has_key(key):
            return cache[key]
        return default
        
    def set(self, key, text):
        self._getCache()[key] = text
        return text
        
    def unset(self, key):
        cache = self._getCache()
        if cache.has_key(key):
            return cache.pop(key)
        return

def testsetup():
    from testing import Filter
    content = type('dummy', (object,), {})()
    content.aq_base = content
    fil = Filter(content)
    fil.fieldname = 'body'
    return content, ContentCacheManager(fil)

if __name__=="__main__":
    import doctest
    doctest.testmod()
