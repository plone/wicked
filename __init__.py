"""
wicked
~~~~~~~~~~

$Id: $
"""

__authors__ = 'Whit Morriss <whit@kalistra.com>, Rob Miller <ra@burningman.com>'
__docformat__ = 'restructuredtext'


from Globals import package_home
from Products.Archetypes import public as atapi
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore import utils as cmf_utils
from Products.CMFCore.DirectoryView import registerDirectory
import config
import sys
from AccessControl import ModuleSecurityInfo
from AccessControl import allow_module, allow_class, allow_type

# Register Global Tools/Services/Config
# (Skins)
registerDirectory(config.SKINS_DIR, config.GLOBALS)

def initialize(context):
    # Importing the content types allows for their registration
    # with the Archetypes runtime
    import example
    #import tools

    # Ask Archetypes to handback all the type information needed
    # to make the CMF happy.
    types = atapi.listTypes(config.PROJECTNAME)
    content_types, constructors, ftis = atapi.process_types( types,
                                                             config.PROJECTNAME)
    from permissions import permissions
    allTypes = zip(content_types, constructors)
    for atype, constructor in allTypes:
        kind = "%s: %s" % (config.PROJECTNAME, atype.archetype_name)
        cmf_utils.ContentInit(
            kind,
            content_types      = (atype,),
            permission         = permissions[atype.portal_type],
            extra_constructors = (constructor,),
            fti                = ftis,
            ).initialize(context)

    ModuleSecurityInfo('Products.wicked.lib.normalize').declarePublic('titleToNormalizedId')
    allow_module('Products.wicked.lib.normalize')
    allow_module('pdb')
    
    ModuleSecurityInfo('Products.wicked.config').declarePublic('BACKLINK_RELATIONSHIP')
    allow_module('Products.wicked.config')


