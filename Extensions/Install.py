"""
mostly borrowed from Bricolite
"""
from StringIO import StringIO
from Products.Archetypes.public import listTypes
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.Extensions.utils import installTypes, install_subskin
from Products.CMFCore.utils import getToolByName
from Products.ZCatalog.ZCatalog import manage_addZCatalog
from OFS.ObjectManager import BadRequestException

from Products.wicked.utils import installDepends
from Products.wicked import config

def configureReferenceCatalog(portal, out):
    catalog = getToolByName(portal, REFERENCE_CATALOG)
    for indexName, indexType in (
        ('targetId', 'FieldIndex'),
        ('targetTitle', 'FieldIndex'),
        ('targetURL', 'FieldIndex'), ):

        try:
            catalog.addIndex(indexName, indexType, extra=None)
        except:
            pass
        try:
            catalog.addColumn(indexName)
        except:
            pass

        catalog.manage_reindexIndex(indexName)


def configureWysiwyg(portal, out):
    editors = portal.portal_properties.site_properties.getProperty('available_editors')
    if "Kupu" in editors:
        # move it up in the list
        editors = list(editors)
        editors.remove('Kupu')
        editors = ['Kupu',] + editors
        portal.portal_properties.site_properties._updateProperty('available_editors', editors)


def install(self):
    out = StringIO()

    installDepends(self)

    install_subskin(self, out, config.GLOBALS)

    installTypes(self, out, listTypes(config.PROJECTNAME), config.PROJECTNAME)

    configureReferenceCatalog(self, out)
    configureWysiwyg(self, out)

    pc = getToolByName(self, 'portal_catalog')
    try:
        pc.addColumn('UID')
    except :
        pass

    print >> out, "Successfully installed %s." % config.PROJECTNAME
    return out.getvalue()
