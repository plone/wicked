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
    
    def __init__(self):
        pass
    
    def scopedSearch(self, scope):
        if self.chunk != 'dud':
            return self.brains
    
    def search(self, chunk, normalized):
        if chunk != 'dud' and chunk != 'scoped':
            return self.brains
        self.chunk = chunk
        self.normalized = normalized

def argchug(rets):
    def function(*args, **kwargs):
        return rets

def fakefilter():
    def conf(*args, **kw):
        self = list(args).pop()
        [setattr(self, k, v) for k, v in kw.items()]
    conf = classmethod(conf)
    kdict = dict(configure=conf)
    wfilter = dummy(kdict, name='wfilter')
    wfilter.query_iface = query
    wfilter.getMatch = argchug(('uid', 'link'))
    wfilter.getSeeker = lambda : query()
    return wfilter
