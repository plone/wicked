from zope.interface import implements, Interface
try:
    from Products.filter.interfaces import IMacroFilter
except ImportError:
    IMacroFilter = Interface

from general import dummy

class Filter(object):
    """
    dummy
    """
    implements(IMacroFilter)
    
    def __init__(self, context):
        self.context = context

    def _filterCore(self, *args, **kwargs):
        pass

    def filter(self, *args, **kwargs):
        pass
    
    section='body'


from Products.wicked.lib.factories import ContentCacheManager     
def cachetestsetup():
    content = dummy({}) 
    content.aq_base = content
    content.absolute_url=lambda : '/you/are/here'
    fil = Filter(content)
    ccm=ContentCacheManager(content)
    ccm.setName(fil.section)
    fil.cache=ccm

    return content, ccm

portal_tools = dict()
def getToolByName(context, toolname, default):
    return portal_tool.get(toolname, default)

def backlinkTools():
    import Products.CMFCore.utils
    Products.CMFCore.utils.getToolByName = getToolByName
    from Products import AdvancedQuery
    from Products.CMFCore.CatalogTool import CatalogTool
    from Products.Archetypes.ReferenceEngine import ReferenceCatalog, UIDCatalog
    return dict(portal_workflow=None,
                portal_catalog=CatalogTool(),
                reference_catalog=ReferenceCatalog(id='portal_reference'),
                portal_uid=UIDCatalog(id='portal_uid'))

def setupTools(tools):
    portal_tools.update(tools)

from general import pdo

## class pRefCat(dict):
##     def _queryFor(self, **kw):
##         self.get(kw['tid']) 

##     def addReference(self, obj, target, *args, **kwargs):
##         attrs= dict(targetUID=target.UID())

##         if not self.has_key(self[obj.UID()]):
##             self[obj.UID()] = []
            
##         self[obj.UID()].append(pdo(attrs))

##     def _resolveBrains(self, suid, tuid, *args):
##         return [x for x in self.get(suid) if x.targetUID==tuid].pop()
    
##    def _deleteReference(self, obj):
##         del self[obj.UID()]
