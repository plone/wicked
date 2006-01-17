from Products.AdvancedQuery import Eq, Generic
from Products.CMFCore.utils import getToolByName
from Products.wicked import config
from filtercore import match
from interfaces import IContentCacheManager, IWickedQuery, IATBacklinkManager, IMacroCacheManager
from normalize import titleToNormalizedId as normalize
from pprint import pformat as format
from relation import Backlink
from zope.interface import implements

class ATBacklinkManager(object):
    implements(IATBacklinkManager)

    relation = config.BACKLINK_RELATIONSHIP
    refKlass = Backlink
    
    def __init__(self, wfilter):
        assert wfilter.fieldname
        self.wfilter = wfilter
        self.context = wfilter.context
        self.renderLink = wfilter.renderLinkForBrain
        self.getBrain = wfilter.getLinkTargetBrain
        self.cm = IMacroCacheManager(self.wfilter)
        self.cat = getToolByName(self.context, 'portal_catalog')
        self.refcat = getToolByName(self.context, 'reference_catalog')
        self.suid = self.context.UID()
        self.template = wfilter.template
        self.wicked_macro = wfilter.wicked_macro

    def getLinks(self):
        """
        Returns dataobjects representing backlinks
        """
        cat = self.cat
        refbrains = self.refcat._queryFor(relationship=self.relation,
                                 tid=self.suid, sid=None)
        if refbrains:
            uids = [brain.sourceUID for brain in refbrains]
            return cat(UID=uids)
        return []


    def set(self, brain, link):
        self.refcat.addReference(brain.getObject(),
                                 self.context,
                                 relationship=self.relation,
                                 referenceClass=self.refKlass)
        uid, rendered = self.wfilter.renderChunk(link, [brain], cache=True)
        self.cm.set((intern(link), brain.UID), rendered)  

    
    def _preplinks(self, links=dict()):
        return links and dict([(normalize(link), link) for link in links]) \
                     or dict()


    def addLinks(self, links, scope, dups=tuple()):
        # asyncing backlinking would help
        dups = set(dups)

        for link in links:
            brain = self.getBrain(link, **dict(scope=scope))
            if isinstance(brain, tuple):
                import pdb; pdb.set_trace()

            if not brain or brain.UID in dups: continue
            self.set(brain, link)


    def manageLinks(self, new_links, scope=None):
        if new_links:
            dups = self.removeLinks(new_links)
            self.addLinks(new_links, scope, dups)


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

            

_marker = object()

class WickedCatalogInquisitor(object):
    """
    CMFish catalog query handler
    """
    implements(IWickedQuery)

    chunk = _marker
    normalled = _marker
    scope = _marker
    
    def __init__(self, context):
        self.context = context # the filter
        content = self.content = context.context
        self.scope = context.scope
        self.catalog = getToolByName(content, 'portal_catalog')
        self.path = '/'.join(content.aq_inner.aq_parent.getPhysicalPath())    
        self.evalQ = self.catalog.evalAdvancedQuery

    @match
    def scopedSearch(self):
        chunk, title = self.chunk, self.title
        query = (Eq('getId', chunk) | Eq('Title', title))
        if not self.scope is _marker:
            # XXX let's move this out of attr storage
            # on the content to at least an annotation
            scope = getattr(self.content, self.scope, self.scope)
            if callable(scope):
                scope = scope()
            if scope:
                query = Generic('path', scope) & query
        return self.evalQ(query, ('created',))

    @match
    def search(self):
        chunk = self.chunk
        normalled = self.normalled
        getId = chunk
        self.title = title = '"%s"' % chunk
        query = Generic('path', {'query': self.path, 'depth': 1}) \
                & (Eq('getId', chunk) | Eq('Title', title) | Eq('getId', normalled))
        result = self.evalQ(query, ('created',))
        return result

    def configure(self, chunk, normalled, scope):
        self.chunk = chunk
        self.normalled = normalled
        self.scope = scope
        
from cache import CacheStore
from zope.app.annotation.interfaces import IAnnotations, IAnnotatable

CACHE_KEY = 'Products.wicked.lib.factories.ContentCacheManager'

class ContentCacheManager(object):

    implements(IContentCacheManager)

    def __init__(self, context):
        self.context = context # the filter
        self.content = context.context # the parent object
        self.name = self.context.fieldname

    def _getStore(self):
        cache_store = getattr(self, 'cache_store', _marker)
        if cache_store == _marker:
            ann = IAnnotations(self.content)
            cache_store = ann.get(CACHE_KEY)
            if not cache_store:
                cache_store = CacheStore(id_=self.content.absolute_url())
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
        if use_uid:
            try:
                key = [tkey for tkey, uid in cache.items() \
                       if uid == key].pop()
            except IndexError:
                return
        
        if cache.has_key(key):
            text = self.get(key)
            del cache[key]
            return text
        return

    def reset(self, uid, text):
        store = self._getStore()
        store.set(uid, text)

