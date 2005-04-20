from Products.CMFCore.CMFCorePermissions import setDefaultRoles
import Products.Archetypes.public as atapi
import config

permissions = {}
types = atapi.listTypes(config.PROJECTNAME)
for atype in  types:
    permission = "%s: Add %s" % (config.PROJECTNAME, atype['portal_type'])
    permissions[atype['portal_type']] = permission

    # Assign default roles
    setDefaultRoles(permission, ('Manager',
                                 'Owner'
                                 )
                    )
