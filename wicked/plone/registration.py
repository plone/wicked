from wicked.registration import SelectiveRegistration
from Products.ATContentTypes.interface import IATNewsItem, IATEvent, IATDocument

def document_reg(site):
    return SelectiveRegistration(site, content=IATDocument)
document_reg.interface = IATDocument
document_reg.type = "Page"

def newsitem_reg(site):
    return SelectiveRegistration(site, content=IATNewsItem)
newsitem_reg.interface = IATNewsItem
newsitem_reg.type = "NewsItem"

def event_reg(site):
    return SelectiveRegistration(site, content=IATEvent)
event_reg.interface = IATEvent
event_reg.type = "Event"

basic_type_regs = document_reg, event_reg, newsitem_reg
