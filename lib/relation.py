##########################################################
#
# Licensed under the terms of the GNU Public License
# (see docs/LICENSE.GPL)
#
# Copyright (c) 2005:
#   - The Open Planning Project (http://www.openplans.org/)
#   - Whit Morriss <whit@kalistra.com>
#   - and contributors
#
##########################################################

"""
BackLink
~~~~~~~~

A type of reference that can be used/extended to provide smarter
inter-document linking. With the support of an editor this can be
quite useful.

"""

__authors__ = 'Whit Morriss <whit@kalistra.com>'
__docformat__ = 'restructuredtext'

from Products.Archetypes import public as atapi
from Products.Archetypes.references import Reference
from Products.wicked import config

class Backlink(Reference):
    """
    A backlink is a reference set on an object when it is referenced by a definite
    wiki-link
    """
    relationship = config.BACKLINK_RELATIONSHIP

    def __init__(self, rID, sID, tID, relationship, **kwargs):
        super(Backlink, self).__init__(rID, sID, tID, relationship, **kwargs)

    def targetURL(self):
        """
        let's stick this in the catalog this to keep things light
        """
        target = self.getTargetObject()
        if target:
            return target.absolute_url()
        return '#'



