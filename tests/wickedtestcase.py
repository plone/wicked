import os
from cStringIO import StringIO
from Testing import ZopeTestCase
from Products.CMFCore.utils  import getToolByName
from Products.PloneTestCase import ptc 
#import cmftc
#from Products.Archetypes.tests.ArchetypesTestCase import ArcheSiteTestCase
from Products.wicked.Extensions.Install import install as installWicked

# monkey patch config into ironicwiki schema
from Products.wicked.example.ironicwiki import schema
schema['body'].wicked_macro='wicked_test'

import Products.wicked.config as config
from Products.wicked.utils import parseDepends, doc_file
from Products.wicked.api import titleToNormalizedId
from Products.filter.tests.filtertestcase import fivezcml, filterzcml, setUp, tearDown, zcml, FilterTestCase
from Products.wicked.lib import field
import Products.wicked


def setupCA():
    tearDown()
    setUp()
    fivezcml.loadmeta()
    fivezcml.load('permissions.zcml')
    #fivezcml.zcml.load_config('configure.zcml', Products.wicked)
    fivezcml.zcml.load_config('configure.zcml', Products.wicked.lib)
    
    # once we have a filter directive
    #filterzcml.loadmeta()
    fivezcml.clear()
    

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

USELXML = False

# This is the test case. You will have to add test_<methods> to your
# class in order to assert things about your Product.
class WickedTestCase(FilterTestCase):
    
    def afterSetUp(self):
        super(WickedTestCase, self).afterSetUp()
        
        # add some pages
        self.page1 = makeContent(self.folder,
                                 titleToNormalizedId(TITLE1),
                                 self.wicked_type, title=TITLE1)
        self.page2 = makeContent(self.folder,
                                 titleToNormalizedId(TITLE2),
                                 self.wicked_type, title=TITLE2)

    def strip(self, text):
        """
        if lxml is available, use it to strip out whitespace
        """
        text = text.strip()
        if not text:
            return text
        try:
            from lxml import etree
        except ImportError:
            return text

        # ganked from zopt and sfive

        xsltfile = os.path.join(os.path.dirname(__file__), 'strip.xsl')
        xslt = file(xsltfile)
        xslt_doc = etree.parse(xslt)
        style = etree.XSLT(xslt_doc)

        textfile = StringIO(text)
        doc = etree.parse(textfile)
        result = style.apply(doc)
        return style.tostring(result)

    def getRenderedWickedField(self, doc):
        fieldname = self.wicked_field
        text = field.WikiField.get(doc.getField(fieldname), doc)
        return self.strip(text)

    def failIfAddLink(self, doc):
        """ does wicked field text contain a wicked-generated add link? """
        # XXX make test stronger, support looking for specific links
        home_url= doc.absolute_url()
        text = self.getRenderedWickedField(doc)
        if home_url in text:
            self.fail("%s FOUND:\n\n %s" %(home_url, text))

    def failUnlessAddLink(self, doc):
        """ does wicked field text contain a wicked-generated add link? """
        # XXX make test stronger, support looking for specific links
        home_url= doc.absolute_url()
        text = self.getRenderedWickedField(doc)
        if not home_url in text:
            self.fail("%s NOT FOUND:\n\n %s" %(home_url, text))

    def failIfWickedLink(self, doc, dest):
        dest = dest.absolute_url()
        text = self.getRenderedWickedField(doc)
        if dest in text:
            self.fail("%s FOUND:\n\n %s" %(dest, text))

    def failUnlessWickedLink(self, doc, dest):
        dest = dest.absolute_url()
        text = self.getRenderedWickedField(doc)
        if not dest in text:
            self.fail("%s NOT FOUND:\n\n %s" %(dest, text))

    def hasAddLink(self, doc):
        """ does wicked field text contain a wicked-generated add link? """
        # XXX make test stronger, support looking for specific links
        return doc.absolute_url() in self.getRenderedWickedField(doc)

    def hasWickedLink(self, doc, dest):
        """ does wicked field text contain a resolved wicked link to
        the specified dest object?  """
        # XXX make test stronger
        return dest.absolute_url() in self.getRenderedWickedField(doc)

ptc.setupPloneSite(products=['Archetypes', 'wicked'], required_zcml=setupCA)
