##########################################################
#
# Licensed under the terms of the GNU Public License
# (see docs/LICENSE.GPL)
#
# Copyright (c) 2005:
#   - The Open Planning Project (http://www.openplans.org/)
#   - Whit Morriss <whit@kalistra.com>
#   - and contributors
#
##########################################################

"""
IronicWiki
~~~~~~~~~~

a demonstration of wicked's capabilities confined to the content type
wicked aspires to make obsolete

"""

__authors__ = 'Whit Morriss <whit@kalistra.com>'
__docformat__ = 'restructuredtext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes import public as atapi
from Products.wicked import config as config
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName

from Products.filter import api as fapi
from Products.wicked import api as wapi

schema = atapi.BaseSchema.copy() + atapi.Schema((
    wapi.WikiField( "body",
                    primary=True,
                    filters=('Wicked Filter',),
                    default_content_type='text/structured',
                    default_output_type='text/html',
                    allowable_content_types = ('text/structured',
                                               'text/restructured',
                                               'text/html',
                                               'text/plain',
                                               'text/plain-pre'),
                    
                    widget=atapi.RichWidget( description = "Link away!",
                                             description_msgid = "help_body_text",
                                             label = "The wiki",
                                             label_msgid = "label_body_text",
                                             rows = 25,
                                             i18n_domain = "plone")),
    
    ))
     

class IronicWiki(atapi.BaseContent):
    """ Ironic wiki Portal Content """

    archetype_name = portal_type = meta_type = 'IronicWiki'
    schema=schema
    global_allow=True

atapi.registerType(IronicWiki, config.PROJECTNAME)
