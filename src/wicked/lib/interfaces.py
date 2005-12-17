from zope.interface import Interface, Attribute
from Products.filter.interfaces import IMacroFilter

class IWickedFilter(IMacroFilter):
    """
    Wicked field filter
    """

class IMacroCacheManager(Interface):

    def get(key, default, **kwargs):
        """
        @rendered wicked link
        """
        
    def set(key, text):
        """
        sets text to cache
        """
        
    def unset(key):
        """
        invalidates cache key
        """

class IContentCacheManager(IMacroCacheManager):
    """
    a cache manager that cache per content instance
    on the content type itself. It manages a dual level data
    structure: dict(fieldname=dict(key=value))
    """
    cache_attr = Attribute('attribute to access cache through')
    fieldname = Attribute('attribute to access sub-cache through')

    def _getStore():
        """
        create and / or
        @return the  master store
        """
        
    def _getCache():
        """
        @return actual datastructure
        for getting and setting
        """
        
class IWickedQuery(Interface):
    """
    object for handling and returning
    dataobjects for wicked prep
    for the macro parser
    """

