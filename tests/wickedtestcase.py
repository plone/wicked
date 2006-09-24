import os
from cStringIO import StringIO
from Testing import ZopeTestCase
from Testing.ZopeTestCase import PortalTestCase
from Products.CMFCore.utils  import getToolByName
from Products.PloneTestCase import ptc 
from collective.testing.layer import ZCMLLayer 
from Products.Archetypes.tests.atsitetestcase import ATSiteTestCase

from Products.wicked.Extensions.Install import install as installWicked

# monkey patch config into ironicwiki schema
from Products.wicked.example.ironicwiki import schema
schema['body'].wicked_macro='wicked_test'

import Products.wicked.config as config
from Products.wicked.utils import parseDepends, doc_file
from Products.wicked.lib.testing.xml import xstrip as strip
from Products.wicked.api import titleToNormalizedId
from Products.wicked.lib import field

from zope.app.apidoc.component import getProvidedAdapters as gpa
from zope.interface import Interface

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
class WickedTestCase(ATSiteTestCase):

    def afterSetUp(self):
        # add some pages
        self.page1 = makeContent(self.folder,
                                 titleToNormalizedId(TITLE1),
                                 self.wicked_type, title=TITLE1)
        self.page2 = makeContent(self.folder,
                                 titleToNormalizedId(TITLE2),
                                 self.wicked_type, title=TITLE2)

    strip = staticmethod(strip)
 
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

    failIfMatch = failIfWickedLink

    def failUnlessWickedLink(self, doc, dest):
        dest = dest.absolute_url()
        text = self.getRenderedWickedField(doc)
        if not dest in text:
            self.fail("%s NOT FOUND:\n\n %s" %(dest, text))

    failUnlessMatch = failUnlessWickedLink

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
