from relation import Backlink
from normalize import titleToNormalizedId
from Products.wicked import config
from Products.filter import api as fapi

from Products.Archetypes import public as atapi
from Products.Archetypes.Registry import registerField

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression
from Products.CMFCore.Expression import createExprContext

from AccessControl import ClassSecurityInfo

try:
    # When Reference are in CMFCore
    from Products.CMFCore.reference_config import *
    from Products.CMFCore.ReferenceCatalog import Reference
    from Products.CMFCore.Referenceable import Referenceable
except ImportError:
    # And while they still live in Archetypes
    from Products.Archetypes.ReferenceEngine import Reference
    from Products.Archetypes.Referenceable import Referenceable
    from Products.Archetypes.config import REFERENCE_CATALOG as REFERENCE_MANAGER
    from Products.Archetypes.config import UID_CATALOG as UID_MANAGER

from filter import pattern as linkregex 

def normalize(wikilink, remove_parens=False):
    wikilink.replace('((', '')
    wikilink.replace('))', '')
    return titleToNormalizedId(wikilink)

class WikiField(fapi.FilterField):
    """ drop-in wiki """
    
    __implements__ = fapi.FilterField.__implements__
    _properties = fapi.FilterField._properties.copy()
    _properties.update({
        'filter':'Wicked Filter',

        # scope, template, and wicked_macro would work nicely as TALS
        
        'scope': '',
        'template': 'wicked_link',
        'wicked_macro':'wicked_link'
        })
    
    security  = ClassSecurityInfo()
    def get(self, instance, mimetype=None, raw=False, **kwargs):
        """
        Pass in a scope, template and macro, then let filter field do it's magic
        """
        kwargs['scope'] = self.scope
        kwargs['template'] = self.template
        kwargs['wicked_macro'] = self.wicked_macro
        return fapi.FilterField.get(self, instance, mimetype=mimetype,
                                    raw=raw, **kwargs)
        
    def set(self, instance, value, **kwargs):
        """
        do a normal text field set, then parse to set backlink references,
        and to remove stale backlinks
        """
        
        fapi.FilterField.set(self, instance, value, **kwargs)        

        # parse wiki text, set backlinks
        if value.__class__ == atapi.BaseUnit:
            value_str = value.getRaw()
        else:
            value_str = value
        new_links = linkregex.findall(value_str)
        old_links = instance.getBRefs(relationship=config.BACKLINK_RELATIONSHIP)

        new_links = map(normalize, new_links)
        
        # add appropriate backlinks, remove stale ones
        if new_links:
            catalog = getToolByName(instance, UID_MANAGER)
            brains = filter(None, catalog(id=new_links))

            refcat = getToolByName(instance, REFERENCE_MANAGER)

            # replace with generator expression
            [ refcat.addReference( brain.getObject(),
                                   instance,
                                   relationship=config.BACKLINK_RELATIONSHIP,
                                   referenceClass=Backlink) \
              for brain in brains ]

        new_links = [ (link, True) for link in new_links ]
        unlink = [ obj for obj in old_links \
                     if not dict(new_links).has_key(obj.id) ]

        [ obj.deleteReference(instance, relationship=config.BACKLINK_RELATIONSHIP)
          for obj in unlink ]

registerField(WikiField,
              title='Wiki',
              description='Text field capable of wiki style behavior')
