from Products.Five import BrowserView

class WickedLink(BrowserView):
    """
    
    """
    def __init__(self, context, request):
        self._context = (context,)
        self.request = request
        
    @property
    def context(self):
        return self._context[0]


