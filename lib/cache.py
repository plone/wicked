"""
A simple mapping layer

This could eventually act as the link editing storage
"""
from persistent import Persistent
from persistent.mapping import PersistentMapping
from BTrees.OOBTree import OOBTree

_marker = object()

class CacheStore(Persistent):
    """
    basic persistent cache object

    see cache.txt
    """
    def __init__(self, id_):
        self.id = id_
        super(CacheStore, self).__init__(self)
        self.field={}
        self._cache = OOBTree()

    def __repr__(self):
        name = self.__class__.__name__
        name = "%s '%s'" %(name, self.id)
        return "%s %s :: %s" %(name, self.field, [x for x in self._cache.items()])

    def get(self, key, default=None):
        return self._cache.get(key, default)

    def set(self, key, text):
        self._cache[key] = text
        self._p_changed

    def getCache(self, key):
        subcache = self.field.get(key, _marker)
        if subcache is _marker:
            cache = Cache(parent=self, id_=self.id)
            self.field[key] = cache
            subcache = self.field[key]
            self._p_changed
        return subcache
        
    def remove(self, key):
        val = self._cache.get(key)
        if val:
            del self._cache[key]
            self._p_changed=True

class Cache(PersistentMapping):

    def __init__(self, id_=None, parent=None):
        self.parent = parent
        self.id = id_
        self._reverse={}
        super(Cache, self).__init__()

    def getRaw(self, key):
        return super(Cache, self).__getitem__(key)

    def parentGet(self, uid, default=None):
        return self.parent.get(str(uid), default)

    def get(self, key, default=None):
        uid = super(Cache, self).get(key, default)
        return self.parentGet(uid, default)

    def set(self, key, text):
        slug, uid = key
        self[slug] = uid
        self._reverse[uid] = slug
        self.parent.set(uid, text)
        self._p_changed
        return text
        
    def __getitem__(self, key):
        retval = self.parentGet(key)
        if retval: return retval
        return self.getRaw(key)

    def __repr__(self):
        rep = super(Cache, self).__repr__()
        name = self.__class__.__name__
        name = "%s '%s'" %(name, self.id)
        return "%s %s" %(name, rep)

    def __delitem__(self, key):
        """
        trickle up deletion
        """
        uid = self.getRaw(key)
        self.parent.remove(key)
        
        super(Cache, self).__delitem__(key)
