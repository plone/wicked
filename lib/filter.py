import sre
from Products.filter import api as fapi
from Products.CMFCore.utils import getToolByName

from normalize import titleToNormalizedId

pattern = sre.compile('\(\(([\w\W]+?)\)\)') # matches ((Some Text To link 123))

class WickedFilter(fapi.MacroSubstitutionFilter):
    """
    Filter for creating core wiki behavior 
    """

    name='Wicked Filter'
    pattern=pattern

    def _filterCore(self, instance, chunk, **kwargs):
        """ Use the portal catalog to find a list of possible links.
        fiter by path, present by macro"""

        catalog = getToolByName(instance, 'portal_catalog')
        
        scope = kwargs['scope'].copy() # could be replaced with a tals eval or full object
        scope['Title'] = titleToNormalizedId(chunk)

        kwargs['links'] = [ (brain.getPath(), brain.getIcon)
                            for brain in catalog(**scope) ]
        kwargs['chunk'] = chunk
        macro = kwargs['wicked_macro']; del kwargs['wicked_macro']
        return self._macro_renderer(instance, macro, **kwargs)
    
fapi.registerFilter(WickedFilter())
