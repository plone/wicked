##Script (Python) "addByWikiLink"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=type_name, Title
##title=used to add content by wiki link
##
if type_name is None:
    raise Exception, 'Type name not specified'

if Title is None:
    raise Exception, 'Title not specified'

from Products.wicked.lib.normalize import titleToNormalizedId
from Products.wicked.config import BACKLINK_RELATIONSHIP

newcontentid=titleToNormalizedId(Title)
newcontentid = container.invokeFactory(type_name, id=newcontentid)
newcontent = getattr(container, newcontentid)

# if new content is referenceable
if container.portal_interface.objectImplements\
   (newcontent,
    'from Products.Archetypes.interfaces.referenceable.IReferenceable'):
    newcontent.addReference(context, relationship=BACKLINK_RELATIONSHIP)
    
