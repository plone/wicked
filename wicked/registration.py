from wicked.at.seeker import IWickedQuery, AdvQueryMatchingSeeker
from wicked.cache import ICacheManager, ContentCacheManager
from wicked.txtfilter import WickedFilter, IWickedFilter
from wicked.txtfilter import IAmWickedField, IFieldEvent
from wicked.txtfilter import BrackettedWickedFilter
from wicked import utils
from wicked.fieldevent.interfaces import IFieldRenderEvent, IFieldStorageEvent
from wicked.interfaces import IAmWicked
from wicked.interfaces import IAmWickedField
from wicked.interfaces import IWickedFilter
from wicked.interfaces import IWickedEvent

from wicked.txtfilter import BrackettedWickedFilter
from wicked.txtfilter import WickedFilter, wicked_listener
from zope.app.schema.vocabulary import IVocabularyFactory
from zope.component import getSiteManager
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary

try:
    import pkg_resources
    get_points = pkg_resources.iter_entry_points
except ImportError:
    get_points = []

class BaseWickedRegistration(object):
    """abstract base: add a docstring to display a description on the
    wicked dashboard"""
    title = "((Basic))"
    field = IAmWickedField
    content = IAmWicked
    event = IFieldRenderEvent
    txtfilter = WickedFilter
    txtfilter_provides = IWickedFilter
    subscriber = (wicked_listener,)
    
    def __init__(self, context, **kw):
        self.site = context
        for key, item in kw.items():
            if hasattr(self, key):
                setattr(self, key, item)

    @utils.memoizedproperty
    def sm(self):
        return getSiteManager(self.site)

    @property
    def required(self):
        return (self.field, self.content, self.event)
    
    def handle(self, unregister=False):
        # @@ add logging
        handle_adapter_reg = self.sm.registerAdapter
        handle_subscriber_reg = self.sm.registerHandler
        if unregister:
            handle_adapter_reg = self.sm.unregisterAdapter
            handle_subscriber_reg = self.sm.unregisterHandler
        
        self.handle_txtfilter(handle_adapter_reg)
        handle_subscriber_reg(self.subscriber[0], required=self.required)
        return (handle_adapter_reg, handle_subscriber_reg)
    
    def unregister(self):
        # @@ add logging
        self.handle_txtfilter(unregister=True)
        self.sm.unregisterHandler(self.subscriber[0], required=self.required)

    def handle_txtfilter(self, handle, event=None, txtfilter=None, unregister=False):
        """helper for common reg of txtfilter"""
        txtfilter = txtfilter and txtfilter or self.txtfilter
        required = list(self.required)
        if event:
            required[2] = event

        handle(self.txtfilter,
               required=required,
               provided=self.txtfilter_provides)

    def is_installed(self):
        raise NotImplemented


class BasePloneWickedRegistration(BaseWickedRegistration):
    """Basic wicked behavior for Plone. Registers a fieldevent
    subscriber and the wicked filter."""

class BasePloneMediaWickedRegistration(BasePloneWickedRegistration):
    """Same as basic but with square bracket style linking"""
    title = "[[Bracketted]]"
    txtfilter = BrackettedWickedFilter

class SelectiveRegistration(BaseWickedRegistration):
    """by dropping direct registration to IAmWicked for content, we
    can selectively turn on and off the creation of wiki behavior by
    content interface. To do this though, we have to hand register a
    seeker and a cache manager"""
    cache = ContentCacheManager
    cache_provides = ICacheManager
    seeker = AdvQueryMatchingSeeker
    seeker_provides = IWickedQuery
    other_events = (IWickedEvent, IFieldStorageEvent)

    @property
    def cache_required(self):
        return (self.txtfilter_provides, self.content)
    
    def handle(self, unregister=False):
        handle_adapter_reg, handle_subscriber_reg = super(SelectiveRegistration, self).handle(unregister=unregister)
        self.handle_cache(handle_adapter_reg)
        self.handle_seeker(handle_adapter_reg)
        for event in self.other_events:
            self.handle_txtfilter(handle_adapter_reg, event=event)
        return (handle_adapter_reg, handle_subscriber_reg)

    def handle_cache(self, handle):
        handle(self.cache,
               required=self.cache_required,
               provided=self.cache_provides)

    def handle_seeker(self, handle):
        handle(self.seeker,
               required=(self.content,),
               provided=self.seeker_provides)
    

## vocabulary

# @@ this will have to wait since plone does not have an egg story yet

class BaseConfigurationOptionsFactory(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        entry_points = get_points("wicked.base_registration")
        items = [(bc.name, bc.load().title) for bc in entry_points]
        items.sort()
        items.insert(0, ('off', 'Off'))
        return SimpleVocabulary.fromItems(items)

class CacheConfigurationOptionsFactory(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        return SimpleVocabulary.fromItems(list())


CacheConfigurationOptions = CacheConfigurationOptionsFactory()
BaseConfigurationOptions = BaseConfigurationOptionsFactory()

