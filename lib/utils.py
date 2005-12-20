from Products.CMFCore.utils import getToolByName
from normalize import titleToNormalizedId

def getRelativePath(path, instance):
    """
    Get path relative to portal
    """
    portal_path = getToolByName(instance,
                               'portal_url').getPortalPath().split('/')
    path = path.split('/')
    return '/'.join(path[len(portal_path):])

def packBrain(brain, context):
    return {'path': brain.getPath(),
            'icon': brain.getIcon,
            'rel_path': getRelativePath(brain.getPath(), context)}

def linkresult(matcher):
    def newGetMatch(self, chunk, brains, **kw):
        link_brain = matcher(self, chunk, brains, **kw)
        return_brain = kw.get('return_brain', False)
        if return_brain and link_brain:
            return link_brain.UID, link_brain

        if link_brain:
            return link_brain.UID, packBrain(link_brain, self.context)
        
        return None, None
    return newGetMatch

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

## doc_path = self.context.absolute_path()
##     all = brains
##     count = 1
##     while doc_path:
##         doc_path.pop()
##         brains = [brain for brain in brains \
##                   if tuple(brain.getPath().split('/')[:-count]) == \
##                   tuple(doc_path]
        
                  

    btup = [(brain.getId, brain) for brain in brains]
    btup.reverse()
    id_dict = dict(btup)
    for unk in normalled_chunk, chunk:
        if id_dict.has_key(unk):
            return id_dict[unk]

    brains = [brain for brain in brains if intern(titleToNormalizedId(brain.Title)) is normalled_chunk]
    return brains and brains[0] or None
