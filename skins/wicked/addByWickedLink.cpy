##Script (Python) "addByWikiLink"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=type_name="", Title=""
##title=used to add content by wiki link
##
if not Title:
    raise Exception, 'Title not specified'

if not type_name:
    type_name = context.portal_type
    #raise Exception, 'Type name not specified'

from Products.wicked.lib.normalize import titleToNormalizedId
from Products.wicked.config import BACKLINK_RELATIONSHIP

newcontentid = titleToNormalizedId(Title)
# XXX this is ambiguous as to where content will end up depending
#     on whether 'context' is folderish
context.invokeFactory(type_name, id=newcontentid,
                      title=Title)
newcontent = getattr(context, newcontentid)

# if new content is referenceable
if context.portal_interface.objectImplements\
   (newcontent,
    'Products.Archetypes.interfaces.referenceable.IReferenceable'):
    newcontent.addReference(context, relationship=BACKLINK_RELATIONSHIP)

state.set(status='success', context=newcontent,
          portal_status_message='"%s" has been created' % Title)
return state
