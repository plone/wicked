from Testing                 import ZopeTestCase
from Products.CMFCore.utils  import getToolByName
from Products.PloneTestCase import setup

from Products.Archetypes.tests.ArchetypesTestCase import ArcheSiteTestCase
from Products.wicked.Extensions.Install import install as installWicked

import Products.wicked.config as config
from Products.wicked.utils import parseDepends, doc_file
from Products.wicked.api import titleToNormalizedId

# Dynamic bootstapping based on product config
def installConfiguredProducts():
    config, handler = parseDepends()

    def registerProduct(values):
        for pkg in values:
            ZopeTestCase.installProduct(pkg, 0)

    handler({'required' : registerProduct,
             'optional' : registerProduct,
             })
    # and finally ourselves
    ZopeTestCase.installProduct('wicked')

installConfiguredProducts()

# util for making content in a container
def makeContent(container, id, portal_type, title=None):
    container.invokeFactory(id=id, type_name=portal_type)
    o = getattr(container, id)
    if title is not None:
        o.setTitle(title)
    return o

TITLE1 = "Cop Shop"
TITLE2 = 'DMV Computer has died'

# This is the test case. You will have to add test_<methods> to your
# class inorder to assert things about your Product.
class WickedTestCase(ArcheSiteTestCase):
    
    def afterSetUp(self):
        ArcheSiteTestCase.afterSetUp(self)
        installWicked(self.portal)
        
        # Because we add skins this needs to be called. Um... ick.
        self._refreshSkinData()

        # add some pages
        self.page1 = makeContent(self.folder,
                                 titleToNormalizedId(TITLE1),
                                 'IronicWiki', TITLE1)
        self.page2 = makeContent(self.folder,
                                 titleToNormalizedId(TITLE2),
                                 'IronicWiki',TITLE2)

setup.PortalSetup(products=['Archetypes', 'wicked'])
