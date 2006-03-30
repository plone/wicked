from zope.app.event.interfaces import IObjectEventw
from zope.interface import implements, Interface

class IWickedAddEvent(IObjectEvent):
    """
    
    """



class WickedAddEvent(object):
    """ An object has been added via wicked """
    implements(IWickedAddEvent)
    
    def __init__(self, obj):
        self.object = obj
        
    
def handleTargetDeletion(obj, event):
    """
    """
    import pdb; pdb.set_trace()


def handleTargetMove(obj, event):
    """
    """
    import pdb; pdb.set_trace()
