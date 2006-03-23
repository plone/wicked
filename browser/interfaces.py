from zope.interface import Interface

class WickedLink(Interface):

    def context():
        """
        context
        """
        
    def howmany():
        """
        @return integer
        how many links
        """
        
    def multiple():
        """
        @return boolean
        howmany > 1
        """

    def links():
        """
        @return list
        list of link datum
        """

    def singlelink():
        """
        @return boolean
        howmany == 1
        """

    def load(links, chunk, section):
        """
        load data for repeated rendering
        """
