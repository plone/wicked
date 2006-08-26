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

from Products.wicked.utils import getFilter
from Products.txtfilter import api as fapi

from Products.Archetypes import public as atapi
from Products.Archetypes.Registry import registerField

from Products.CMFCore.utils import getToolByName

from txtfilter import WickedFilter
from txtfilter import pattern as linkregex 
from utils import removeParens

class WikiField(fapi.FilterField):
    """ drop-in wiki """
    
    __implements__ = fapi.FilterField.__implements__
    _properties = fapi.FilterField._properties.copy()
    _properties.update({
        'filter':WickedFilter.name,
        'scope': '',
        })
    
    security  = ClassSecurityInfo()
    def get(self, instance, mimetype=None, raw=False, **kwargs):
        """
        Pass in a scope, template and macro, then let filter field do it's magic
        """
        # configuration
        kwargs['scope'] = self.scope
        kwargs['section'] = self.getName()
        return super(WikiField, self).get(instance, mimetype=mimetype,
                                          raw=raw, **kwargs)
        
    def set(self, instance, value, **kwargs):
        """
        do a normal text field set, set backlink references, remove stale
        backlinks, cache resolved forward links
        """
        super(WikiField, self).set(instance, value, **kwargs)        

        # parse wiki text, set backlinks
        
        value_str = value
        if value.__class__ == atapi.BaseUnit:
            value_str = value.getRaw()
        elif value.__class__ == FileUpload:
            # a file was uploaded, get the (possibly transformed) value
            value_str = self.get(instance, skip_filters=True)

        found = linkregex.findall(value_str)

        if not len(found):
            return

        config = dict(section=self.getName(),
                      scope=self.scope)
        wicked = getFilter(instance)
        wicked.configure(**config)
        new_links = [removeParens(link) for link in found]
        wicked.manageLinks(new_links)

registerField(WikiField,
              title='Wiki',
              description='Text field capable of wiki style behavior')
