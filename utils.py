from Products.CMFCore.utils import getToolByName
from Products.filter import api as fapi
from Products.wicked.config import FILTER_NAME
from StringIO import StringIO
from ZODB.POSException import ConflictError
from os.path import join, abspath, dirname, basename
from zope.component import getAdapter

import ZConfig
import os.path

def getFilter(obj):
    return getAdapter(obj, fapi.IFieldFilter, FILTER_NAME)

## Configuration utilities
DIR_PATH = abspath(dirname(__file__))

def conf_file(file):
    return join(DIR_PATH, 'conf', file)

def doc_file(file):
    return join(DIR_PATH, 'docs', file)

def register(portal, pkg):
    qi = getToolByName(portal, 'portal_quickinstaller')
    if not qi.isProductInstalled(pkg):
        install = qi.installProduct(pkg)

def requires(portal, pkg):
    """Make sure that we can load and install the package into the
    site"""
    register(portal, pkg)

def optional(portal, pkg):
    try:
        register(portal, pkg)
        return True
    except ConflictError:
        raise
    except:
        return False

def parseDepends():
    schema = ZConfig.loadSchema(conf_file('depends.xml'))
    config, handler = ZConfig.loadConfig(schema,
                                         conf_file('depends.conf'))
    return config, handler

def installDepends(portal):
    config, handler = parseDepends()
    # Curry up some handlers
    def required_handler(values, portal=portal):
        for pkg in values:
            requires(portal, pkg)

    def optional_handler(values, portal=portal):
        for pkg in values:
            optional(portal, pkg)

    handler({'required' : required_handler,
             'optional' : optional_handler,
             })

