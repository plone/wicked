from Products.wicked.interfaces import IWickedTarget
from Products.Five.utilities.marker import mark
from Products.wicked.lib.interfaces import IWickedBacklink 
from Products.wicked import config
from Products.CMFCore.utils import getToolByName

def upgrade09(site):
    refcat = getToolByName(site, 'reference_catalog')
    refs = (brain.getObject() for brain in \
               refcat(relationship=config.BACKLINK_RELATIONSHIP))
    
    for ref in refs:
        if ref:
            obj=ref.getSourceObject()
            mark(obj, IWickedTarget)
            if not IWickedBacklink.providedBy(ref):
                print ref
                mark(ref, IWickedBacklink)
