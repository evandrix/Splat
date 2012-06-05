__all__ = [ 'LazyLoader' ]


class LazyLoader(object):

    """Abstract base for lazy loaders of persistent features"""

    def load(self, ob, attrName):
        """Load 'ob' at least with 'attrName'

        Note that a lazy loader is allowed to load all the attributes it
        knows how to, as long as it only overwrites *itself* in the object's
        dictionary.  That is, if an attribute to be read has already been
        written to, it should not reload that attribute.

        This method is not required to return a value, and it can ignore
        the 'attrName' parameter as long as it is certain that the 'attrName'
        attribute will be loaded.
        """
        raise NotImplementedError

