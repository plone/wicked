from zope.interface import Interface
from Products.filter.interfaces import IFilterable, IFieldFilter
from zope.app.annotation.interfaces import IAttributeAnnotatable


class IAmWicked(IFilterable, IAttributeAnnotatable):
    """
    wicked content...

    note that this interface is not required for wicked to work, just
    to distinguish particular objects as intending to use wicked
    for some processing
    """


class IWickedFilter(IFieldFilter):
    """
    Wicked field filter
    """


class IWickedTarget(Interface):
    """
    marker interface for an object linked to in a wicked text area
    """
