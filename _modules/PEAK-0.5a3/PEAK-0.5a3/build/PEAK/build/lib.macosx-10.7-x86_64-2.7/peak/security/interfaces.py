from peak.api import NOT_GIVEN, protocols
from protocols import Interface, Attribute
from peak.util.imports import whenImported
from types import FunctionType

__all__ = [
    'IAuthorizedPrincipal', 'IInteraction', 'IAccessAttempt',
    'IAbstractPermission', 'IAbstractPermission', 'IPermissionChecker',
    'IGuardedObject', 'IGuardedClass', 'IGuardedDescriptor',
]

class IAccessAttempt(Interface):

    """An attempt to access a protected object"""

    user = Attribute("""Application user object""")

    principal = Attribute("""IAuthorizedPrincipal for the attempt""")

    interaction = Attribute("""IInteraction for the attempt""")

    permission = Attribute(
        """Concrete permission type to be checked"""
    )

    subject = Attribute("""The object to which access is desired""")

    name = Attribute(
        """The name of the sub-object of 'subject' to which acess is desired

        (May be 'None' if access to 'subject' itself is desired.)"""
    )

    def allows(subject=NOT_GIVEN, name=NOT_GIVEN, permissionNeeded=NOT_GIVEN,
        user=NOT_GIVEN
    ):
        """True if 'user' has 'permissionNeeded' for 'subject', or Denial()"""




class IAuthorizedPrincipal(Interface):

    """A principal (e.g. user) w/global grants or denials of permission

    In addition to permission checks based on business rules, it may be
    desirable to globally grant or deny a permission for a given principal.
    If this is the case, providing an adapter from your user object class
    to 'IAuthorizedPrincipal' will allow the user object to participate
    in permission checks via the 'checkGlobalPermission()' method.
    """
    
    def checkGlobalPermission(attempt):
        """Does principal have a global grant or deny of 'attempt.permission'?

        Return NOT_FOUND if there is no knowledge of a global grant or denial
        of 'permType'.  Otherwise return truth to grant permission, or
        a false value to deny it.

        Note that principals are not responsible for local grants/denials."""






















class IInteraction(Interface):

    """Component representing a security-controlled user/app interaction

    An interaction provides the necessary context to identify what security
    rules should be used, and on whose behalf the action is being performed
    (i.e. the principal).  To determine if an access is allowed, you use the
    interaction's 'allows()' method.

    To determine what set of security rules are to be applied, an
    interaction supplies a 'permissionProtocol' attribute, to which
    abstract and concrete permissions will be adapted for checking.  In the
    simple case, 'IPermissionChecker' is used as this 'permissionProtocol'.
    However, if one application extends a library or another application that
    provides default security rules registered under 'IPermissionChecker',
    the new application may wish to set the 'permissionProtocol' to a
    'protocols.Variation' of 'IPermissionChecker', in order to declare
    new rules that take precedence over the defaults.  For example::

        myRulesProtocol = protocols.Variation(IPermissionChecker)

        class MyRuleSet(security.RuleSet):
            # declare rules that override default rules

        MyRuleSet.declareRulesFor(myRulesProtocol)
        
        anInteracton = security.Interaction(
            parentComponent,
            permissionProtocol = myRulesProtocol,
            user = someUser
        )
        
    The application could then check whether 'someUser' has permissions
    for various objects, using the rules defined for 'myRulesProtocol'
    (with fallback to any rules defined for 'IPermissionChecker').
    
    """




    user = Attribute("""The IPrincipal responsible for the interaction""")

    permissionProtocol = Attribute(
        """The protocol to which permissions should be adapted for checking"""
    )

    def allows(subject,name=None,permissionNeeded=NOT_GIVEN,user=NOT_GIVEN):
        """Return true if 'user' has 'permissionNeeded' for 'subject'

        If 'user' is not supplied, the interaction's user should be used.  If
        the permission is not supplied, 'subject' should be adapted to
        'IGuardedObject' in order to obtain the required permission.

        Note that if 'subject' does not support 'IGuardedObject', and the
        required permission is not specified, then this method should always
        return true when the 'name' is 'None', and false otherwise.  That is,
        an unguarded object is accessible, but none of its attributes are.
        (This is so that value objects such as numbers and strings don't need
        permissions.)

        This method should return a true value, or a 'security.Denial()' with
        an appropriate 'message' value."""



class IPermissionChecker(Interface):

    """An object that can verify the presence of a permission"""

    def checkPermission(attempt):
        """Does the principal for 'attempt' have the needed permission?

        This method may return any false value to indicate failure, but
        returning a 'security.Denial()' is preferred."""







# Permission interfaces

class IConcretePermission(Interface):

    """An abstract permission applied to a specific object type

    For example, "View content of Document" or "Content Manager of Folder".
    Concrete permissions allow separate security rules to be declared for
    an abstract permission, based on the type of object being accessed.
    The 'addRule' method of a concrete permission is used to define
    security rules for concrete permissions.  (Note: abstract permissions
    are actually concrete permissions themselves; they are roughly equivalent
    to concrete permissons on the type 'object'.)
    """

    def getAbstract():
        """Return an IAbstractPermission for this permission"""

    def addRule(rule,protocol=IPermissionChecker):
        """Declare 'rule' an adapter factory from permission to 'protocol'"""

    __mro__ = Attribute(
        """Sequence of this type's supertypes, itself included, in MRO order"""
    )

    def defaultDenial():
        """Return a default security.Denial() to be used when a check fails"""














class IAbstractPermission(IConcretePermission):

    """A conceptual permission, group, or role

    For example, "View content", or "Content Manager" would be "abstract
    permissions".  The easiest way to create an abstract permission is to
    subclass 'security.Permission', e.g.::

        class ViewContent(security.Permission):
            "Permission to view an object's content"

    That's all that's needed, since abstract permissions are simply a marker
    that denotes the *idea* of a particular permission.
    
    """
    
    def of(protectedObjectType):
        """Return a subclass IConcretePermission for 'protectedObjectType'"""























# Protected-Object interfaces

class IGuardedObject(Interface):

    """Object that knows permissions needed to access subobjects by name"""

    def getPermissionForName(name):
        """Return (abstract) permission needed to access 'name', or 'None'"""


class IGuardedClass(Interface):

    """Class that can accept permission declarations for its attributes"""

    def declarePermissions(objectPerm=None, **namePerms):
        """Declare permissions for named attributes"""

    def getAttributePermission(name):
        """Return (abstract) permission needed to access 'name', or 'None'"""


class IGuardedDescriptor(Interface):

    """Descriptor that knows the permission required to access it"""

    permissionNeeded = Attribute(
        "Sequence of abstract permissions needed, or 'None' to keep default"
    )













whenImported(
    'peak.binding.once',
    lambda once:
        protocols.declareAdapter(
            protocols.NO_ADAPTER_NEEDED,
            provides = [IGuardedDescriptor],
            forTypes = [once.Descriptor, once.Attribute]
        )
)

whenImported(
    'peak.model.features',
    lambda features:
        protocols.declareAdapter(
            protocols.NO_ADAPTER_NEEDED,
            provides = [IGuardedDescriptor],
            forTypes = [features.FeatureClass]
        )
)

protocols.declareAdapter(
    # Functions can be guarded descriptors if they define 'permissionsNeeded'
    lambda o,p: (getattr(o,'permissionNeeded',None) is not None) and o or None,
    provides = [IGuardedDescriptor],
    forTypes = [FunctionType]
)















