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

A type of reference that can be used/extened to provide smarter
inter-document linking. With the support of an editor this can be
quite useful.

"""

__authors__ = 'Whit Morriss <whit@kalistra.com>'
__docformat__ = 'restructuredtext'

from Products.Archetypes import public as atapi
from Products.wicked import config as config
from Products.Archetypes.references import Reference
from Products.filter.api import getFilter

class Backlink(Reference):
    """
    A backlink is a reference set on an object when it is reference by a definite
    wiki-link
    """
    relationship = config.BACKLINK_RELATIONSHIP

    def targetURL(self):
        """
        let's stick this in the catalog this to keep things light
        """
        target = self.getTargetObject()
        if target:
            return target.absolute_url()
        return '#'

    

