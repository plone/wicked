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
def makeContent(container, id, portal_type, **kw):
    container.invokeFactory(id=id, type_name=portal_type, **kw)
    o = getattr(container, id)
    return o

TITLE1 = "Cop Shop"
TITLE2 = 'DMV Computer has died'

wf1_contents = {
    'wicked-one': {'Type': 'IronicWiki',
                   'title': 'Wicked One'},
    'wicked-two': {'Type': 'IronicWiki',
                   'title': 'Wicked Two'},
    'wicked-three': {'Type': 'IronicWiki',
                     'title': 'Wicked Three'},
    }

wf2_contents = {
    'wicked-one': {'Type': 'IronicWiki',
                   'title': 'Wicked One'},
    'wicked-two-diff-id': {'Type': 'IronicWiki',
                           'title': 'Wicked Two'},
    'wicked-three': {'Type': 'IronicWiki',
                     'title': 'Wicked Three Different Title'},
    }

wf3_contents = {
    'wicked-one': {'Type': 'IronicWiki',
                   'title': 'Wicked One'},
    'wicked-two': {'Type': 'IronicWiki',
                   'title': 'Wicked Two'},
    }    

test_content = {
    'wf1': {'Type': 'Folder',
            'title': 'WickedFolder1',
            'contents': wf1_contents},
    'wf2': {'Type': 'Folder',
            'title': 'WickedFolder2',
            'contents': wf2_contents},
    'wf3': {'Type': 'Folder',
            'title': 'WickedFolder3',
            'contents': wf3_contents},
    }

# This is the test case. You will have to add test_<methods> to your
# class in order to assert things about your Product.
class WickedTestCase(ArcheSiteTestCase):
    
    def afterSetUp(self):
        ArcheSiteTestCase.afterSetUp(self)
        installWicked(self.portal)
        
        # Because we add skins this needs to be called. Um... ick.
        self._refreshSkinData()

        # add some pages
        self.page1 = makeContent(self.folder,
                                 titleToNormalizedId(TITLE1),
                                 'IronicWiki', title=TITLE1)
        self.page2 = makeContent(self.folder,
                                 titleToNormalizedId(TITLE2),
                                 'IronicWiki',title=TITLE2)

    def createTestContent(self):
        for f_id, f_desc in test_content.items():
            folder = makeContent(self.folder, f_id, f_desc['Type'],
                                 title=f_desc['title'])
            setattr(self, f_id, folder)
            for ob_id in f_desc['contents'].keys():
                ob_desc = f_desc['contents'][ob_id]
                makeContent(folder, ob_id, ob_desc['Type'],
                            title=ob_desc['title'])

setup.PortalSetup(products=['Archetypes', 'wicked'])
