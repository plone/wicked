from Products.ATContentTypes.migration.walker import CatalogWalker
from Products.wicked.migration.migrator import WickedDocMigrator
from Products.CMFCore.utils import getToolByName

def migrate_atdoc_wickeddoc(self):
    catalog = getToolByName(self, 'portal_catalog')
    migrators = (WickedDocMigrator,)
    out = []

    for migrator in migrators:
        out.append('*** Migrating %s to %s ***\n' % (migrator.src_portal_type,
                                                     migrator.dst_portal_type))
        w = CatalogWalker(migrator, catalog)
        out.append(w.go())

        wf = getToolByName(self, 'portal_workflow')
        count = wf.updateRoleMappings()
        out.append('Workflow: %d object(s) updated.' % count)
    
        catalog.refreshCatalog(clear=1)
        out.append('Portal catalog updated.')

        atct_tool = getToolByName(self, 'portal_atct')
        atct_tool._changePortalTypeName('Document', 'ATDocument',
                                        global_allow=0,
                                        title='AT Document')
        atct_tool._changePortalTypeName('WickedDoc', 'Document',
                                        global_allow=1,
                                        title='Document')
        out.append('Document types switched')

        return '\n'.join(out)

