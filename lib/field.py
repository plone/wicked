##########################################################
#
# Licensed under the terms of the GNU Public License
# (see docs/LICENSE.GPL)
#
# Copyright (c) 2005:
#   - The Open Planning Project (http://www.openplans.org/)
#   - Whit Morriss <whit@kalistra.com>
#   - Rob Miller <rob@kalistra.com> (RaFromBRC)
#   - and contributors
#
##########################################################

from AccessControl import ClassSecurityInfo
from ZPublisher.HTTPRequest import FileUpload

from relation import Backlink
from normalize import titleToNormalizedId
from filter import WickedFilter
from Products.wicked import config
from Products.filter import api as fapi

from Products.Archetypes import public as atapi
from Products.Archetypes.Registry import registerField

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression
from Products.CMFCore.Expression import createExprContext

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
        'filter':WickedFilter.name,

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
        do a normal text field set, set backlink references, remove stale
        backlinks, cache resolved forward links
        """
        
        fapi.FilterField.set(self, instance, value, **kwargs)        

        # parse wiki text, set backlinks
        if value.__class__ == atapi.BaseUnit:
            value_str = value.getRaw()
        elif value.__class__ == FileUpload:
            # a file was uploaded, get the (possibly transformed) value
            value_str = self.get(instance, skip_filters=True)
        else:
            value_str = value

        new_links = linkregex.findall(value_str)
        old_links = instance.getBRefs(relationship=config.BACKLINK_RELATIONSHIP)

        new_links = map(normalize, new_links)
        
        # add appropriate backlinks, remove stale ones
        if new_links:
            kwargs['scope'] = self.scope
            wkd_filter = fapi.getFilter(WickedFilter.name)
            getLTB = wkd_filter.getLinkTargetBrain
            brains = [getLTB(instance, new_link, **kwargs) \
                      for new_link in new_links]
            brains = filter(None, brains)

            refcat = getToolByName(instance, REFERENCE_MANAGER)

            # replace with generator expression
            for brain in brains:
                refcat.addReference(brain.getObject(),
                                    instance,
                                    relationship=config.BACKLINK_RELATIONSHIP,
                                    referenceClass=Backlink)

        new_links = dict([(link, True) for link in new_links])
        unlink = [obj for obj in old_links \
                  if not new_links.has_key(obj.id)]

        for obj in unlink:
            obj.deleteReference(instance,
                                relationship=config.BACKLINK_RELATIONSHIP)

registerField(WikiField,
              title='Wiki',
              description='Text field capable of wiki style behavior')
