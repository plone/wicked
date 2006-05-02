##########################################################
#
# Licensed under the terms of the GNU Public License
# (see docs/LICENSE.GPL)
#
# Copyright (c) 2005:
#   - The Open Planning Project (http://www.openplans.org/)
#   - Whit Morriss <whit at www.openplans.org>
#   - and contributors
#
##########################################################
from urllib import quote
from zope.interface import Interface
from Products.Five import BrowserView
from Products.CMFFormController.ControllerBase import ControllerBase

from Products.wicked.lib.normalize import titleToNormalizedId as normalize
from Products.wicked.config import BACKLINK_RELATIONSHIP
from Products.wicked.utils import getFilter
from Products.wicked.lib.interfaces import IContentCacheManager, IBacklinkManager

_marker=object()

class WickedAdd(BrowserView):

    def __init__(self, context, request):
        self._context = (context,)
        self.request = request
        
    @property
    def context(self):
        return self._context[0]

    def addContent(self, title=None, section=None, type_name=_marker):
        # make it possible to pass in container
        # pre-populate with backlinks?
        type_name = self.request.get('type_name', type_name)
        if type_name is _marker:
            type_name = self.context.portal_type
        title = self.request.get('Title', title)
        section = self.request.get('section', section)
        assert title, 'Must have a title to create content' 
        newcontentid = normalize(title)

        # put the new object at the same level as the context
        # XXX this will only work w/ Z2-style acquisition
        # XXX the property trick above isn't working, context still comes
        # back wrapped in the view :-(
        parent = self._context[0].aq_parent
        parent.invokeFactory(type_name, id=newcontentid,
                             title=title)

        # XXX move marker to own package, add notifier
        # make this handled by an event
        newcontent = getattr(self.context, newcontentid)
        wicked = getFilter(self.context)
        wicked.section=section
        wicked.manageLink(newcontent, title)
        
        portal_status_message='"%s" has been created' % title
        url = newcontent.absolute_url()
        restr = "%s/edit?portal_status_message=%s" %(url, quote(portal_status_message))
        return self.request.RESPONSE.redirect(restr)

    def addMenu(self):
        return 1
