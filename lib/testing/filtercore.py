from general import dummy

def fakecacheiface(cached):
    def call(*args):
        return args[0]
    def set(*args):
        return "<link cached>"
    methods = dict(__call__=call, set=set) 
    cacheman=type('dummy',
                  (dict,), methods)()
    cacheman.update(cached)
    return cacheman

class query(object):
    
    brains = ['We are brains!']
    
    def __init__(self, chunk, normalized, scope):
        self.configure(chunk, normalized, scope)
    
    def scopedSearch(self):
        if self.chunk != 'dud':
            return self.brains
        
    def configure(self, chunk, normalized, scope):
        self.chunk = chunk
        self.normalized = normalized
        self.scope = scope
        
    def search(self):
        if self.chunk != 'dud' and self.chunk != 'scoped':
            return self.brains

def argchug(rets):
    def function(*args, **kwargs):
        return rets
    
def fakefilter():
    def conf(*args, **kw):
        self = list(args).pop()
        [setattr(self, k, v) for k, v in kw.items()]
        return kw
    conf = classmethod(conf)
    localizeSlug = classmethod(lambda self, x:
                           x.replace(self.url_signifier, 'http://fakeurl/'))
    kdict = dict(configure=conf, url_signifier="$$", localizeSlug=localizeSlug, scope='/scope/')
    wfilter = dummy(kdict, name='wfilter')
    wfilter.query_iface = query
    wfilter.getMatch = argchug(('uid', 'link'))
    wfilter.getSeeker = lambda chunk, normalized: query(chunk, normalized, wfilter.scope)
    return wfilter
