from Products.AdvancedQuery import Eq, Generic
from Products.Archetypes.interfaces import IReferenceable
from Products.CMFCore.utils import getToolByName
from Products.Five.utilities.marker import mark
from Products.wicked import config
from Products.wicked.interfaces import IWickedTarget
from cache import CacheStore
from interfaces import IContentCacheManager, IWickedQuery, IATBacklinkManager
from normalize import titleToNormalizedId as normalize
from relation import Backlink
from utils import memoizedproperty, memoize, match
from zope.app.annotation.interfaces import IAnnotations, IAnnotatable
from zope.interface import implements


class ATBacklinkManager(object):
    implements(IATBacklinkManager)

    relation = config.BACKLINK_RELATIONSHIP
    refKlass = Backlink
    
    def __init__(self, wfilter, context):
        self.wfilter = wfilter
        self.context = context
        self.cm = wfilter.cache
        self.resolver = wfilter.resolver
        self.getMatch = wfilter.getMatch
        ## ATism: remove ASAP
        self.refcat = getToolByName(self.context, 'reference_catalog')
        self.suid = self.context.UID()

    def getLinks(self):
        """
        Returns dataobjects representing backlinks
        """
        refbrains = self.refcat._queryFor(relationship=self.relation,
                                 tid=self.suid, sid=None)
        if refbrains:
            uids = [brain.sourceUID for brain in refbrains]
            ## XXX non-orthogonal
            return self.resolver.queryUIDs(uids)
        return []
    
    def _preplinks(self, links=dict()):
        return links and dict([(normalize(link), link) for link in links]) \
                     or dict()

    def manageLinks(self, new_links):
        # asyncing backlinking would help
        # this has been heavily optimized
        scope=self.wfilter.scope
        dups = set(self.removeLinks(new_links))

        resolver = self.resolver

        norm=tuple()
        for link in new_links:
            normalled=normalize(link)
            norm+=normalled,
            self.resolver.aggregate(link, normalled, scope)

        for link, normalled in zip(new_links, norm):
            match = self.getMatch(link, resolver.agg_brains, normalled=normalled)
            if not match:
                match = self.getMatch(link, resolver.agg_scoped_brains, normalled=normalled)
            if not match or match.UID in dups: continue
            self.manageLink(match, normalled)

    def manageLink(self, obj, normalled):
        if hasattr(obj, 'getObject'):
            # brain, other sort of pseudo object
            obj = obj.getObject()

        if not IReferenceable.providedBy(obj):
            # backlink not possible
            return

        mark(obj, IWickedTarget)
        self.refcat.addReference(obj,
                                 self.context,
                                 relationship=self.relation,
                                 referenceClass=self.refKlass)
        
        path = '/'.join(obj.getPhysicalPath())
        data = dict(path=path,
                    icon=obj.getIcon(),
                    uid=obj.UID())
        
        self.cm.set((intern(normalled), obj.UID()), [data])  

    def removeLinks(self, exclude=tuple()):
        oldlinks = self.getLinks()
        if not oldlinks:
            return set()
        
        exclude = self._preplinks(exclude)        
        dups = set([brain for brain in oldlinks if \
                    self.match(brain, exclude.get)])
        
        [self.remove(brain) for brain in set(oldlinks) - dups]
        return [b.UID for b in dups]

    def match(self, brain, getlink):
        """
        mmmm....turtle. 
        """
        link = getlink(brain.getId,
                       getlink(normalize(brain.Title),
                               None))
        if link:
            return True
                
    def remove(self, brain):
        objs = self.refcat._resolveBrains(\
            self.refcat._queryFor(self.suid, brain.UID, self.relation))
        for obj in objs:
            self.refcat._deleteReference(obj)
            self.cm.unset(obj.targetUID(), use_uid=True)

    def unlink(self, uid):
        self.cm.remove(uid)


_marker = object()
class AdvQueryMatchingSeeker(object):
    """
    An advanced query specific 
    CMFish catalog query handler
    """
    implements(IWickedQuery)

    chunk = _marker
    normalled = _marker
    scope = _marker
    
    def __init__(self, context):
        self.context = context
        self.catalog = getToolByName(context, 'portal_catalog')
        self.path = '/'.join(context.aq_inner.aq_parent.getPhysicalPath())    
        self.evalQ = self.catalog.evalAdvancedQuery

    def configure(self, chunk, normalled, scope):
        self.chunk = chunk
        self.normalled = normalled
        self.scope = scope

    def _query(self, query, sort=('created',)):
        if sort:
            return self.evalQ(query, sort)
        else:
            return self.evalQ(query)

    def queryUIDs(self, uids):
        return self._query(Generic('UID', uids), sort=None)

    @property
    def scopedQuery(self):
        chunk, title = self.chunk, self.title
        query = (Eq('getId', chunk) | Eq('Title', title))
        if not self.scope is _marker:
            # XXX let's move this out of attr storage
            # on the content to at least an annotation
            scope = getattr(self.context, self.scope, self.scope)
            if callable(scope):
                scope = scope()
            if scope:
                query = Generic('path', scope) & query
        return query

    @property
    def basicQuery(self):
        chunk, normalled = self.chunk, self.normalled
        getId = chunk
        self.title = title = "%s" % chunk
        query = Generic('path', {'query': self.path, 'depth': -1}) \
                & (Eq('getId', chunk) | Eq('Title', title) | Eq('getId', normalled))
        return query

    @property
    @match
    def scopedSearch(self):
        return self._query(self.scopedQuery)

    @property
    @match
    def search(self):
        return self._query(self.basicQuery)

    def _aggquery(self, name, query):
        curr = getattr(self, name, _marker)
        if curr is _marker:
            curr = query
        else:
            curr |= query
        setattr(self, name, curr)
        return curr

    @property
    def bquery(self):
        return self._aggquery('_bquery', self.basicQuery)

    @property
    def squery(self):
        return self._aggquery('_squery', self.scopedQuery)


    # memo prevents dups
    @memoize 
    def aggregate(self, link, normalled, scope):
        """
        builds aggregated queries for scoped and basic
        """
        self.configure(link, normalled, scope)
        self.bquery 
        self.squery 

    @memoizedproperty
    def agg_brains(self):
        """
        aggregregate search returns
        """
        return self._query(self._bquery)

    @memoizedproperty
    def agg_scoped_brains(self):
        """
        aggregregate search returns
        """
        return self._query(self._squery)

    __call__ = _query
        
CACHE_KEY = 'Products.wicked.lib.factories.ContentCacheManager'

class ContentCacheManager(object):
    implements(IContentCacheManager)
    def __init__(self, context):
        self.context = context

    def setName(self, name):
        self.name = name

    def _getStore(self):
        cache_store = getattr(self, 'cache_store', _marker)
        if cache_store == _marker:
            ann = IAnnotations(self.context)
            cache_store = ann.get(CACHE_KEY)
            if not cache_store:
                cache_store = CacheStore(id_=self.context.absolute_url())
                ann[CACHE_KEY] = cache_store
            self.cache_store = cache_store 
        return cache_store
 
    def _getCache(self):
        store = self._getStore()
        cache = store.getCache(self.name)
        return cache
    
    def get(self, key, default=None):
        cache = self._getCache()
        return cache.get(key, default)
        
    def set(self, key, text):
        cache = self._getCache()
        cache.set(key, text)
        return text
        
    def unset(self, key, use_uid=False):
        cache = self._getCache()
        val = None
        if use_uid:
            for tkey, uid in cache.items():
                if uid == key:
                    val = self.get(tkey)
                    del cache[tkey]

        if cache.has_key(key):
            val = self.get(key)
            del cache[key]

        return val
    
    def remove(self, uid):
        store=self._getStore()
        store.remove(uid)

    def reset(self, uid, value):
        store = self._getStore()
        store.set(uid, value)

