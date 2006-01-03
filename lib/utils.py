try:
    from Products.CMFCore.utils import getToolByName
except ImportError:
    from testing.general import getToolByName

def removeParens(wikilink):
    wikilink.replace('((', '')
    wikilink.replace('))', '')
    return wikilink
 
def getRelativePath(path, instance):
    """
    Get path relative to portal
    """
    portal_path = getToolByName(instance,
                                'portal_url').getPortalPath().split('/')
    path = path.split('/')
    return '/'.join(path[len(portal_path):])

## def delsetif(obj, attr, argdict, marker):
##     """
##     remove a value from a dict and set it on an
##     object if it is currently unset or the marker

##     >>> _marker = object()
##     >>> inst = type('dummy', (object,), {})()
##     >>> inst.dog = _marker
##     >>> inst.dog is _marker
##     True
##     >>> kw = dict(bob=1, dog=2)
##     >>> [delsetif(inst, key, kw, _marker) for key in kw.keys()]
##     [None, None]
##     >>> inst.dog
##     2
##     >>> inst.bob
##     1
##     >>> kw
##     {}
##     """
##     value = argdict.pop(attr)
##     if getattr(obj, attr, marker) is marker:
##         setattr(obj, attr, value)


if __name__=="__main__":
    import doctest
    doctest.testmod()
