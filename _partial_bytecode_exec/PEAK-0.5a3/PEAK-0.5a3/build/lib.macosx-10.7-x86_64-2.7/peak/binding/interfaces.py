"""PEAK Component Binding Interfaces"""

from protocols import Interface, Attribute
from peak.config.interfaces import IConfigMap, IConfigSource
from peak.api import NOT_GIVEN

__all__ = [
    'IComponentFactory', 'IBindingNode', 'IComponent', 'IRecipe',
    'IBindableAttrs', 'IComponentKey', 'IAttachable', 'IActiveDescriptor'
]


class IComponentKey(Interface):

    """Key that can be looked up via 'Component.lookupComponent()'"""

    def findComponent(context, default=NOT_GIVEN):
        """Look self up in 'context', return 'default' or raise 'NameNotFound'

        'context' is an arbitrary component, to be used as the starting point
        for the search.  'default' is a value to be returned if the key cannot
        be found.  If 'default' is 'NOT_GIVEN', and the key cannot be found,
        this method should raise 'exceptions.NameNotFound' instead of returning
        a value."""


class IRecipe(Interface):

    """3-argument callable that returns a value"""

    def __call__(obj, instDict, attrName):
        """Return a value for the attribute 'attrName' of 'obj'

        'instDict' is the instance dictionary ('__dict__') of 'obj'."""







class IComponentFactory(Interface):

    """Class interface for creating bindable components"""

    def __call__(parentComponent, componentName=None, **attrVals):
        """Create a new component

        The default constructor signature of a binding component is
        to receive an parent component to be bound to, an optional name
        relative to the parent, and keyword arguments which will be
        placed in the new object's dictionary, to override the specified
        bindings.

        Note that some component factories (such as 'binding.Component')
        may be more lenient than this interface requires, by allowing you to
        omit the 'parentComponent' argument.  But if you do not know this is
        true for the object you are calling, you should assume the parent
        component is required."""


class IBindingNode(IConfigSource):

    """Minimum requirements to join a component hierarchy"""

    def getParentComponent():
        """Return the parent component of this object, or 'None'"""

    def getComponentName():
        """Return this component's name relative to its parent, or 'None'"""

    def notifyUponAssembly(child):
        """Call 'child.uponAssembly()' when component knows its root"""









class IBindableAttrs(Interface):

    """Support for manipulating bindable attributes

    (peak.model's 'StructuralFeature' classes rely on this interface.)"""

    def _getBindingFuncs(attrName, useSlot=False):
        """XXX"""

    def _hasBinding(attr,useSlot=False):
        """Return true if binding named 'attr' has been activated"""

    def _getBinding(attr,default=None,useSlot=False):
        """Return binding named 'attr' if activated, else return 'default'"""

    def _setBinding(attr,value,useSlot=False):
        """Set binding 'attr' to 'value'"""

    def _delBinding(attr,useSlot=False):
        """Ensure that no binding for 'attr' is active"""


class IAttachable(Interface):

    """Object that can be told it has a parent component"""

    def setParentComponent(parentComponent,componentName=None,suggest=False):
        """Set the object's parent to 'parentComponent' (or suggest it)

        If 'suggest' is true, this should not change an already-specified
        parent.  If 'suggest' is false, and the current parent has already been
        used by the component for any purpose, this method should raise an
        'AlreadyRead' exception.

        The component's 'componentName' will only be set if the parent is
        successfully set."""





class IComponent(IAttachable, IBindingNode, IBindableAttrs, IConfigMap):

    """API supplied by binding.Component and its subclasses"""

    def lookupComponent(name, default=NOT_GIVEN, adaptTo=None,
        suggestParent=True, creationName=None):
        """Look up 'name' in context - see 'binding.lookupComponent()'"""

    def uponAssembly():
        """Notify the component that its parents and root are known+fixed"""



class IActiveDescriptor(Interface):

    """Metadata supplied by active descriptors (e.g. binding.Attribute)"""

    offerAs = Attribute(
        """Sequence of config keys that this attribute binding offers"""
    )

    uponAssembly = Attribute(
        """Activate this attribute binding when object knows all its parents"""
    )

    def activateInClass(klass, attrName):
        """Do any necessary installation in 'klass' under name 'attrName'"""














