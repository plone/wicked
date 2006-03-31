from Products.wicked import config, utils

def handleTargetDeletion(ref, event):
    """
    Invalidate any pointer before object deletion
    """
    target = ref.getTargetObject()
    wicked = utils.getFilter(target)
    wicked.unlink(ref.sourceUID)


def handleTargetMove(obj, event):
    """
    when a target of a link is moved, or renamed we need to notify any
    objects that may be caching pointers
    """
    #import pdb; pdb.set_trace()
    refs=obj.getRefs(relationship=config.BACKLINK_RELATIONSHIP)
    for ref in refs:
        wicked = utils.getFilter(obj)
        uid = obj.UID()
        path = '/'.join(obj.getPhysicalPath())
        data = dict(path=path,
                    icon=obj.getIcon(),
                    uid=uid)
        wicked.cache.uidset(uid, data)

    
