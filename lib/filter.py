import sre
from Products.filter import api as fapi
from Products.CMFCore.utils import getToolByName

from normalize import titleToNormalizedId

pattern = sre.compile('\(\(([\w\W]+?)\)\)') # matches ((Some Text To link 123))

class WickedFilter(fapi.MacroSubstitutionFilter):
    """
    Filter for creating core wiki behavior 
    """

    name = 'Wicked Filter'
    pattern = pattern

    def getPathRelToPortal(self, path, instance):
        portal_path = getToolByName(instance,
                                    'portal_url').getPortalPath().split('/')
        path = path.split('/')
        return '/'.join(path[len(portal_path):])

    def _filterCore(self, instance, chunk, **kwargs):
        """ Use the portal catalog to find a list of possible links.
        fiter by path, present by macro"""

        catalog = getToolByName(instance, 'portal_catalog')
        
        scope = kwargs['scope'].copy() # could be replaced with a tals eval or full object
        scope.update({'id': chunk,
                     'path': instance.aq_inner.aq_parent.absolute_url_path()})
        brains = catalog(**scope)
        if not brains:
            scope.update({'id': titleToNormalizedId(chunk)})
            brains = catalog(**scope)
            if not brains:
                del scope['id']
                scope.update['Title'] = '"%s"' % chunk
                brains = catalog(**scope)

        kwargs['links'] = [ {'path': brain.getPath(),
                             'icon': brain.getIcon,
                             'rel_path': self.getPathRelToPortal(brain.getPath(),
                                                                 instance)}
                            for brain in brains ]
        kwargs['chunk'] = chunk
        macro = kwargs['wicked_macro']; del kwargs['wicked_macro']
        return self._macro_renderer(instance, macro, **kwargs)
    
fapi.registerFilter(WickedFilter())
