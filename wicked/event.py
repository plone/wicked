from zope.component import handle
from wicked.interface import IWickedEvent

@adapter(IWickedEvent)
def redispatch(event):
    handle(event.context, event)
