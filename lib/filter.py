import sre
from Products.CMFCore.utils import getToolByName
from Products.filter import api as fapi
from Products.AdvancedQuery import Eq, Generic

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

    def _getBrainIdMatch(self, value, brains):
        """
        Return first brain from the sequence w/ id matching specified
        value, or None if no match
        """
        for brain in brains:
            if brain.id == value:
                return brain
        
    def _getBrainTitleMatch(self, value, brains):
        """
        Return first brain from the sequence w/ title matching specified
        value (case insensitive), or None if no match

        Currently just matching on length, since the index lookup was for
        an exact phrase, equal length implies equal value

        XXX do we want to be more forgiving w/ extra whitespace?
        """
        for brain in brains:
            if len(brain.Title) == len(value):
                return brain

    def _filterCore(self, instance, chunk, **kwargs):
        """
        Use the portal catalog to find a list of possible links.
        fiter by path, present by macro
        """
        catalog = getToolByName(instance, 'portal_catalog')
        path = instance.aq_inner.aq_parent.absolute_url_path()
        id = chunk
        title = '"%s"' % chunk
        query = Generic('path', {'query': path, 'depth': 1}) \
                & (Eq('id', id) | Eq('Title', title))
        brains = catalog.evalAdvancedQuery(query, (('created', 'desc'),))
        link_brain = None
        
        if brains:
            if len(brains) == 1:
                link_brain = brains[0]
            else:
                link_brain = self._getBrainIdMatch(chunk, brains)
        else:
            # XXX check for kwargs[scope] and modify path expression in
            #     the following query appropriately
            query = Eq('id', id) | Eq('Title', title)
            brains = catalog.evalAdvancedQuery(query, (('created', 'desc'),))
            if brains:
                if len(brains) == 1:
                    link_brain = brains[0]
                else:
                    link_brain = self._getBrainIdMatch(chunk, brains)

        if brains and not link_brain:
            # there was no id match, get the earliest created Title match
            link_brain = self._getBrainTitleMatch(chunk, brains)

        if link_brain:
            # XXX do we need to support 'links' as a sequence or should
            #     we change to a single 'link'
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
