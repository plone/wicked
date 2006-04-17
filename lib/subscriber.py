##########################################################
#
# Licensed under the terms of the GNU Public License
# (see docs/LICENSE.GPL)
#
# Copyright (c) 2005:
#   - The Open Planning Project (http://www.openplans.org/)
#   - Whit Morriss <whit at www.openplans.org>
#   - and contributors
#
##########################################################
from Products.wicked import config, utils
from zope.app.container.interfaces import IObjectRemovedEvent, IObjectAddedEvent


def handleTargetDeletion(ref, event):
    """
    Invalidate any pointer before object deletion
    """
    target = ref.getTargetObject()
    wicked = utils.getFilter(target)
    wicked.unlink(ref.sourceUID)


def handleTargetMoved(obj, event):
    """
    when a target of a link is moved, or renamed we need to notify any
    objects that may be caching pointers
    """
    # XXX add more tests
    if IObjectRemovedEvent.providedBy(event):
        return
    
    refs=obj.getRefs(relationship=config.BACKLINK_RELATIONSHIP)
    path = '/'.join(obj.getPhysicalPath())
    for ref in refs:
        wicked = utils.getFilter(ref)
        uid = obj.UID()
        data = dict(path=path,
                    icon=obj.getIcon(),
                    uid=uid)
        wicked.cache.reset(uid, [data])

    
