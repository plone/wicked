from zope.interface import Interface, Attribute
from Products.filter.interfaces import IMacroFilter

class IWickedFilter(IMacroFilter):
    """
    Wicked field filter
    """

class IBacklinkManager(Interface):
    """
    this might become the wicked storage manager...
    """
    def manageLinks():
        """
        removes old links adds new
        """

    def addLinks(links, scope, dups=[]):
        """
        retrieves brains, and sets backlinks for a colletion
        wicked links.  will filter against identifiers(UIDs)
        in dups (this allow chaining with removelinks, which
        returns duplicate links)
        """
        
    def getLinks():
        """
        returns all current backlinks
        """
        
    def set(brain, link):
        """
        creates a backlink(a smart pointer pointing for the links target)
        and caches link
        """
        
    def remove(brain):
        """
        does the actual backlink removal and cache unsetting
        """

    def removeLinks(exclude=tuple()):
        """
        iterates over a list of brain representing existing backlink
        and executes backlink deletion if not included in exclude
        
        @exclude: list of strings 'links' not to erase
        """

class IATBacklinkManager(IBacklinkManager):
    """
    A manager for Archetypes reference (aka smart pointer) based backlinka 
    """
    relation = Attribute( """
    Name of Archetype relationship. Used to retrieve
    backlinks from reference engine
    """)


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
    
    chunk = Attribute('unaltered string from inside ((wicked link))')
    normalized = Attribute('normalled chunk')
    scope = Attribute('scoping parameter for "scoped" searches')

    def scopedSearch(best_match):
        """
        @param best_match : attempt to make
        best match for query returned

        @return: list of dataobjects
        """
        
    def search(chunk, normalized, best_match):
        """
        @param best_match : attempt to make
        best match for query returned

        @return : list of dataobjects
        """
        
    def configure(chunk, normalized, scope):
        """
        configure set instance attributes
        
        @param chunk : instance attr 
        @param normalized : instance attr
        @param scope : instance attr

        @return : None
        """
