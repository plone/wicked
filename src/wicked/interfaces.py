from Products.filter.interfaces import IFilterable, IFieldFilter

class IAmWicked(IFilterable):
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
