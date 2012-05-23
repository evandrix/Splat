"""Domain logic and convenience features for manipulating OMG Models

    This module supplies domain logic add-on features for the common
    structural core of CWM, UML, and other OMG metamodels.  Specifically,
    it adds some computed features, such as the notion of a "qualified name"
    of a model element, and the "superclasses" and "subclasses" of
    generalizable elements.  It also gives namespaces a '__getitem__' method
    for easy retrieval of object contents, and a 'find' operation for running
    queries over a model.

    This is basically a pure "advice" module; it should be placed in the
    patch list of an appropriately declared module.
"""

from peak.api import *
from peak.model.queries import query

























class ModelElement:

    class name:
        defaultValue = None


    class qualifiedName(model.DerivedFeature):

        upperBound = 1

        def get(feature,element):

            name = element.name

            if not name:
                return []

            names = list(query([element])['namespace*']['name'])
            names.reverse(); names.append(name)

            return '.'.join(names)


class GeneralizableElement:

    class superclasses(model.DerivedFeature):

        def get(feature,element):
            return list(query([element])['generalization']['parent'])


    class subclasses(model.DerivedFeature):

        def get(feature,element):
            return list(query([element])['specialization']['child'])






class Namespace:

    _contentsIndex = binding.Make(
        lambda self: dict([
            (ob.name, ob) for ob in self.ownedElement
        ])
    )


    class ownedElement:

        def _onLink(feature, element, item, posn=None):
            element._contentsIndex[item.name]=item

        def _onUnlink(feature, element, item, posn=None):
            del element._contentsIndex[item.name]


    def __getitem__(self,key):

        if '.' in key:
            ob = self
            for k in key.split('.'):
                ob = ob[k]
            return ob

        return self._contentsIndex[key]


    def find(self,*criteria):
        q = query(self.ownedElements)
        for c in criteria:
            q = q[c]
        return q







