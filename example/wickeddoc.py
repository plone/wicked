"""
WickedDoc
~~~~~~~~~~

A simple subclass of the ATDocument type that supports wicked
linking in the primary text field.

"""

__authors__ = 'Rob Miller <ra@burningman.com>'
__docformat__ = 'restructuredtext'

from AccessControl import ClassSecurityInfo
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from Products.Archetypes import public as atapi
try:
    from Products.ATContentTypes.atct import ATDocument
except ImportError: # ATCT 0.2
    from Products.ATContentTypes.types.ATDocument import ATDocument
try:
    from Products.ATContentTypes.config import zconf
    ATDOCUMENT_CONTENT_TYPE = zconf.ATDocument.default_content_type
except ImportError: # ATCT 0.2
    from Products.ATContentTypes.config import ATDOCUMENT_CONTENT_TYPE

from Products.filter import api as fapi

from Products.wicked import config as config
from Products.wicked import api as wapi

schema = ATDocument.schema.copy() + atapi.Schema((
    wapi.WikiField('text',
                   required=True,
                   searchable=True,
                   primary=True,
                   filters=('Wicked Filter',),
                   validators = ('isTidyHtmlWithCleanup',),
                   #validators = ('isTidyHtml',),
                   default_content_type = ATDOCUMENT_CONTENT_TYPE,
                   default_output_type = 'text/html',
                   allowable_content_types = ('text/structured',
                                              'text/x-rst',
                                              'text/html',
                                              'text/plain',
                                              'text/plain-pre',
                                              'text/python-source',),
                   widget = atapi.RichWidget(
                        description = "The body text of the document.",
                        description_msgid = "help_body_text",
                        label = "Body text",
                        label_msgid = "label_body_text",
                        rows = 25,
                        i18n_domain = "plone")),
    ))
     

class WickedDoc(ATDocument):
    """ ATDocument with wicked linking """

    archetype_name='Wicked Doc'
    portal_type= meta_type ='WickedDoc'
    schema=schema
    global_allow=True

atapi.registerType(WickedDoc, config.PROJECTNAME)
