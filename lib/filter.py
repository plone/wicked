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

    def _getMatchFromQueryResults(self, chunk, brains):
        """
        Given a set of query results and the wicked link text, return
        the brain that represents the correct object to link to, or
        None

        Assumes that brains are already ordered oldest to newest, so
        the first absolute match is the one returned.  Matches on id
        take priority over matches on title

        Currently title matches comparisons are just testing for equal
        length; since the index lookup was for an exact phrase, equal
        length implies equal value

        XXX do we want to be more forgiving w/ extra whitespace in the
        title?
        """
        link_brain = None
        if len(brains) == 1:
            if brains[0].id == chunk or len(brains[0].Title) == len(chunk):
                link_brain = brains[0]
        else:
            for brain in brains:
                if brain.id == chunk:
                    link_brain = brain
                    break
            if not link_brain:
                # there was no id match, get the earliest created Title match
                for brain in brains:
                    if len(brain.Title) == len(chunk):
                        link_brain = brain
                        break
        return link_brain

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
        brains = catalog.evalAdvancedQuery(query, ('created',))

        link_brain = None
        if brains:
            link_brain = self._getMatchFromQueryResults(chunk, brains)

        if not link_brain:
            # XXX check for kwargs[scope] and modify path expression in
            #     the following query appropriately
            query = Eq('id', id) | Eq('Title', title)
            brains = catalog.evalAdvancedQuery(query, ('created',))
            if brains:
                link_brain = self._getMatchFromQueryResults(chunk, brains)

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
