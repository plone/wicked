"""
Import example types to allow for initialization
"""
from ironicwiki import IronicWiki
try:
    from wickeddoc import WickedDoc
except ImportError: # no ATCT
    pass
