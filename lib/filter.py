import sre
from Products.CMFCore.utils import getToolByName
from Products.filter import api as fapi
from Products.AdvancedQuery import Eq

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

    def _getBrainAttrMatch(self, attr, value, brains,
                           case_sensitive=True):
        """
        Return first brain from the sequence w/ specified attribute
        matching the specified value, or None if no match
        """
        if not case_sensitive:
            value = value.lower()
        for brain in brains:
            b_value = getattr(brain, attr)
            if not case_sensitive:
                b_value = b_value.lower()
            if getattr(brain, attr) == value:
                return brain
        
    def _filterCore(self, instance, chunk, **kwargs):
        """
        Use the portal catalog to find a list of possible links.
        fiter by path, present by macro
        """
        catalog = getToolByName(instance, 'portal_catalog')
        path = instance.aq_inner.aq_parent.absolute_url_path()
        query = Eq('path', path) & (Eq('id', chunk) | Eq('Title', chunk))
        #import pdb; pdb.set_trace()
        brains = catalog.evalAdvancedQuery(query, (('created', 'desc'),))
        link_brain = None
        
        if brains:
            if len(brains) == 1:
                link_brain = brains[0]
            else:
                link_brain = self._getBrainAttrMatch('id', chunk, brains)
        else:
            # XXX check for kwargs[scope] and modify path expression in
            #     the following query appropriately
            query = Eq('id', chunk) | Eq('Title', chunk)
            brains = catalog.evalAdvancedQuery(query, (('created', 'desc'),))
            if brains:
                if len(brains) == 1:
                    link_brain = brains[0]
                else:
                    link_brain = self._getBrainAttrMatch('id', chunk, brains)

        if brains and not link_brain:
            # there was no id match, get the earliest created Title match
            link_brain = self._getBrainAttrMatch('Title', chunk, brains,
                                                 case_sensitive=False)

        if link_brain:
            kwargs['links'] = [ {'path': link_brain.getPath(),
                                 'icon': link_brain.getIcon,
                                 'rel_path': self.getPathRelToPortal(link_brain.getPath(),
                                                                     instance)} ]
        else:
            kwargs['links'] = []
        kwargs['chunk'] = chunk
        macro = kwargs['wicked_macro']; del kwargs['wicked_macro']
        return self._macro_renderer(instance, macro, **kwargs)
    
fapi.registerFilter(WickedFilter())
