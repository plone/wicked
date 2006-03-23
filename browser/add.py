from urllib import quote
from zope.interface import Interface
from Products.Five.utilities.marker import mark
from Products.wicked.interfaces import IWickedTarget
from Products.Five import BrowserView
from Products.CMFFormController.ControllerBase import ControllerBase

from Products.wicked.lib.normalize import titleToNormalizedId as normalize
from Products.wicked.config import BACKLINK_RELATIONSHIP
from Products.wicked.utils import getFilter
from Products.wicked.lib.interfaces import IContentCacheManager

_marker=object()

class WickedAdd(BrowserView):

    def __init__(self, context, request):
        self._context = (context,)
        self.request = request
        
    @property
    def context(self):
        return self._context[0]


    def addContent(self):
        # make it possible to pass in container
        # pre-populate with backlinks?
        type_name = self.request.get('type_name', _marker)
        if type_name is _marker:
            type_name = self.context.portal_type
        title = self.request.get('Title', '')
        section = self.request.get('section', '')
        assert title, 'Must have a title to create content' 
        newcontentid = normalize(title)
        
        # XXX this is ambiguous as to where content will end up depending
        #     on whether 'context' is folderish
        self.context.invokeFactory(type_name, id=newcontentid,
                                   title=title)

        # encapsulate elsewhere?
        newcontent = getattr(self.context, newcontentid)
        if hasattr(newcontent, 'addReference'):
            newcontent.addReference(self.context, relationship=BACKLINK_RELATIONSHIP)
        
        mark(newcontent, IWickedTarget)

        wicked = getFilter(self.context)
        wicked.configure(fieldname=section)
        path = '/'.join(newcontent.getPhysicalPath())
        
        data = dict(path=path,
                    rel_path=self.request.physicalPathToURL(path, True),
                    icon=newcontent.getIcon())
        
        text = wicked._macro_renderer(wicked.macro,
                                      template=wicked.template,
                                      links=[data])
        
        wicked.cache_manager.set((newconent.UID(), newcontentid), text)
        
        portal_status_message='"%s" has been created' % title
        url = newcontent.absolute_url()
        restr = "%s/edit?portal_status_message=%s" %(url, quote(portal_status_message))
        return self.request.RESPONSE.redirect(restr)


    def addMenu(self):
        return 1
