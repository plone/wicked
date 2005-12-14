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

from Products.filter.Extensions.Install import configureWysiwyg
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


def installExtendedPathIndex(portal, out):
    """ change the path index to an ExtendedPathIndex """
    cat = getToolByName(portal, 'portal_catalog')
    index_types = [index['name'] for index in cat.Indexes.filtered_meta_types()]
    if not 'ExtendedPathIndex' in index_types:
        print >> out, '-> WARNING! ExtendedPathIndex NOT installed!'
        return
    index_dict = dict([i[:2] for i in cat.enumerateIndexes()])
    path_index_type = index_dict['path']
    if path_index_type == 'ExtendedPathIndex':
        print >> out, '-> ExtendedPathIndex already installed'
    else:
        cat.delIndex('path')
        cat.addIndex('path', 'ExtendedPathIndex')
        cat.manage_reindexIndex(['path'])
        print >> out, '-> ExtendedPathIndex installed'

def install(self):
    out = StringIO()
    installDepends(self)

    install_subskin(self, out, config.GLOBALS)

    installTypes(self, out, listTypes(config.PROJECTNAME), config.PROJECTNAME)

    installExtendedPathIndex(self, out)

    configureReferenceCatalog(self, out)
    configureWysiwyg(self, out)

    pc = getToolByName(self, 'portal_catalog')
    try:
        pc.addColumn('UID')
    except :
        pass

    print >> out, "Successfully installed %s." % config.PROJECTNAME
    return out.getvalue()
