from Testing                 import ZopeTestCase
from Products.CMFCore.utils  import getToolByName
from Products.PloneTestCase import ptc 
#import cmftc
#from Products.Archetypes.tests.ArchetypesTestCase import ArcheSiteTestCase
from Products.wicked.Extensions.Install import install as installWicked

import Products.wicked.config as config
from Products.wicked.utils import parseDepends, doc_file
from Products.wicked.api import titleToNormalizedId
from Products.filter.tests.filtertestcase import fivezcml, filterzcml, setUp, tearDown, zcml, FilterTestCase
import Products.wicked

def setupCA():
    tearDown()
    setUp()
    fivezcml.loadmeta()
    fivezcml.load('permissions.zcml')
    fivezcml.zcml.load_config('configure.zcml', Products.wicked)

    # once we have a filter directive
    #filterzcml.loadmeta()
    fivezcml.clear()
    

FilterTestCase.setupCA = staticmethod(setupCA)

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

# This is the test case. You will have to add test_<methods> to your
# class in order to assert things about your Product.
class WickedTestCase(FilterTestCase):
#class WickedTestCase(cmftc.SiteTestCase):
    
    def afterSetUp(self):
        super(WickedTestCase, self).afterSetUp()

        # add some pages
        self.page1 = makeContent(self.folder,
                                 titleToNormalizedId(TITLE1),
                                 self.wicked_type, title=TITLE1)
        self.page2 = makeContent(self.folder,
                                 titleToNormalizedId(TITLE2),
                                 self.wicked_type, title=TITLE2)


    def getRenderedWickedField(self, doc):
        fieldname = self.wicked_field
        return doc.getField(fieldname).getAccessor(doc)()

    def hasAddLink(self, doc):
        """ does wicked field text contain a wicked-generated add link? """
        # XXX make test stronger, support looking for specific links
        return doc.absolute_url() in self.getRenderedWickedField(doc)

    def hasWickedLink(self, doc, dest):
        """ does wicked field text contain a resolved wicked link to
        the specified dest object?  """
        # XXX make test stronger
        return dest.absolute_url() in self.getRenderedWickedField(doc)

ptc.setupPloneSite(products=['Archetypes', 'wicked'])
