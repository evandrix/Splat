"""Permissions, Rules, and Interactions"""

from peak.api import *
from interfaces import *

from weakref import WeakKeyDictionary
from protocols.advice import getFrameInfo, addClassAdvisor
from types import ClassType
from peak.binding.components import _Base

__all__ = [
    'AccessAttempt', 'PermissionType', 'Permission', 'RuleSet',
    'Anybody', 'Nobody', 'Interaction', 'allow', 'Denial',
]


def allow(basePerm=None, **nameToPerm):

    """Use in the body of a class to declare permissions for attributes"""

    def callback(klass):
        gc = adapt(klass,IGuardedClass)
        gc.declarePermissions(basePerm,**nameToPerm)
        return klass

    addClassAdvisor(callback)















class Denial(object):

    """Object representing denial of access"""

    __slots__ = 'message'

    def __init__(self,message):
        self.message = message

    def __nonzero__(self):
        # A denial is always a false condition
        return False

    __len__ = __nonzero__

    def __str__(self):
        return str(self.message)

    def __unicode__(self):
        return unicode(self.message)

    def __repr__(self):
        return 'security.Denial(%r)' % self.message


















class GuardedClassAdapter(protocols.Adapter):

    protocols.advise(
        instancesProvide = [IGuardedClass],
        asAdapterForTypes = [type, ClassType]
    )

    def nameToPermissionsMap(self):
        klass = self.subject
        if '_peak_nameToPermissions_map' in klass.__dict__:
            return klass._peak_nameToPermissions_map

        m = {}

        # Ensure that base classes have their act together...
        for base in klass.__bases__:
            if base is object: continue
            adapt(base,IGuardedClass).getAttributePermission(None)

        map(m.update,
            binding.getInheritedRegistries(
                klass,'_peak_nameToPermissions_map'
            )
        )

        for k,v in klass.__dict__.items():
            v = adapt(v,IGuardedDescriptor,None)
            if v is not None and v.permissionNeeded is not None:
                m[k] = v.permissionNeeded

        if m:
            klass._peak_nameToPermissions_map = m

        return m

    nameToPermissionsMap = binding.Make(nameToPermissionsMap)

    def getAttributePermission(self, name):
        """Return (abstract) permission needed to access 'name', or 'None'"""
        return self.nameToPermissionsMap.get(name)

    def declarePermissions(self, objectPerm=None, **namePerms):

        klass = self.subject

        if hasattr(klass,'__subclasses__') and klass.__subclasses__():
            raise TypeError(
                "Can't change permissions on a class with subclasses", klass
            )

        klass._peak_nameToPermissions_map = m = self.nameToPermissionsMap

        m.update(namePerms)
        if objectPerm is not None:
            m[None] = objectPerm

        protocols.declareAdapter(
            NamePermissionsAdapter, provides = [IGuardedObject],
            forTypes = [klass],
        )


class NamePermissionsAdapter(object):

    __slots__ = 'getPermissionForName'

    protocols.advise(
        instancesProvide = [IGuardedObject],
        asAdapterForTypes = [_Base] # base for binding.Component and model.Type
    )

    def __init__(self,ob,proto):
        self.getPermissionForName = adapt(
            ob.__class__,IGuardedClass
        ).getAttributePermission







class AccessAttempt(object):

    """An attempt to access a protected object"""

    __slots__ = [
        'interaction', 'user', 'subject', 'permission', 'principal', 'name',
    ]

    def __init__(self,
        permission, subject, name=None, user=NOT_GIVEN, interaction=NOT_GIVEN
    ):

        try:
            klass = subject.__class__
        except AttributeError:
            klass = type(subject)

        self.subject = subject
        self.permission = permission.of(klass)
        interaction = adapt(interaction,IInteraction,None)

        if interaction is None:
            if user is not NOT_GIVEN:
                interaction = Interaction(user, user=user)
            else:
                interaction = Interaction()

        self.interaction = interaction

        if user is NOT_GIVEN:
            if interaction is not None:
                user = interaction.user
            else:
                user = None

        self.user = user
        self.principal = adapt(user, IAuthorizedPrincipal, None)
        self.name = name



    def allows(self,
        subject=NOT_GIVEN, name=NOT_GIVEN, permissionNeeded=NOT_GIVEN,
        user=NOT_GIVEN, interaction=NOT_GIVEN
    ):
        if subject is NOT_GIVEN:

            subject=self.subject

            if name is NOT_GIVEN:
                name = self.name

        elif name is NOT_GIVEN:
            # Different subject, don't copy our name!  Assume it's None.
            name = None

        if interaction is NOT_GIVEN:
            interaction=self.interaction

        if user is NOT_GIVEN:
            user=self.user

        if permissionNeeded is NOT_GIVEN:
            permissionNeeded=self.permission.getAbstract()

        return interaction.allows(subject,name,permissionNeeded,user)
















class Interaction(binding.Component):

    """Context for an access-controlled interaction (abstract base)"""

    protocols.advise(
        instancesProvide = [IInteraction]
    )

    user = binding.Require(
        "The principal responsible for this interaction"
    )

    accessType         = AccessAttempt
    permissionProtocol = IPermissionChecker     # XXX


    def allows(self, subject,
        name=None, permissionNeeded=NOT_GIVEN, user=NOT_GIVEN
    ):
        if permissionNeeded is NOT_GIVEN:
            guard = adapt(subject,IGuardedObject,None)
            if guard is not None:
                permissionNeeded = guard.getPermissionForName(name)
                if permissionNeeded is None:
                    return False
            elif name is None:
                # Access w/out a name is okay for unprotected objects
                # because none of their named attributes will be accessible!
                return True
            else:
                return False

        attempt = self.accessType(permissionNeeded, subject, name, user, self)
        checker = adapt(attempt.permission, self.permissionProtocol)
        result = checker.checkPermission(attempt)

        if result==False:   # not a denial; supply a default
            return attempt.permission.defaultDenial()

        return result

class PermissionType(binding.ActiveClass):

    """A permission type (abstract and/or concrete)"""

    protocols.advise(
        instancesProvide = [IAbstractPermission]
    )

    abstractBase = None

    __cache = binding.Make(WeakKeyDictionary, attrName='_PermissionType__cache')

    def of(self,protectedObjectType):
        if self.abstractBase is not None:
            return self.abstractBase.of(protectedObjectType)

        try:
            return self.__cache[protectedObjectType]
        except KeyError:
            pass

        bases = protectedObjectType.__bases__
        if not bases:
            bases = self,
        else:
            bases = tuple([self.of(b) for b in bases])

        subtype = self.__class__(
            '%s_of_%s' % (self.__name__,protectedObjectType.__name__),
            bases, {'__module__': self.__module__, 'abstractBase': self}
        )

        self.__cache[protectedObjectType] = subtype
        return subtype


    def addRule(self, rule, protocol=IPermissionChecker):
        protocols.declareAdapter(
            rule, provides=[protocol], forObjects=[self]
        )

    def getAbstract(self):
        if self.abstractBase is None:
            return self
        else:
            return self.abstractBase


    def defaultDenial(self):
        return (self.abstractBase or self).__denial


    __denial = binding.Make(
        lambda self: Denial(
            # XXX I18N issues here...
            self.__doc__ or ("You must have the %s permission." % self.__name__)
        ), attrName = '_PermissionType__denial'
    )


class Permission:
    """Base class for permissions"""
    __metaclass__ = PermissionType



















class RuleSet(binding.Singleton):

    def checkPermission(klass, attempt):

        if attempt.principal is not None:

            check = attempt.principal.checkGlobalPermission(attempt)

            if check is not NOT_FOUND:
                return check

        # Lookup the right method to call

        reg = klass.__methodNames

        for key in attempt.permission.__mro__:
            if key in reg:
                return getattr(klass,reg[key])(attempt)

        raise NotImplementedError(
            "No rule method found", permissionType
        )


    def asAdapter(klass, permType, protocol):
        return klass


    def declareRulesFor(klass, protocol):
        factory = klass.asAdapter
        for permType in klass.__methodNames:
            permType.addRule(factory, protocol)









    def __methodNames(klass):

        # XXX check completeness/correctness of coverage?

        newMethods = {}

        for k,v in klass.rules:

            for permType in v:

                if permType not in newMethods:
                    newMethods[permType] = k
                    continue

                raise TypeError(
                    "Permission checked by two methods in class:",
                    permType, newMethods[permType], k
                )

        methodNames = {}
        for reg in binding.getInheritedRegistries(
            klass,'_RuleSet__methodNames'
        ):
            methodNames.update(reg)

        methodNames.update(newMethods)
        return methodNames

    __methodNames = binding.Make(__methodNames)












class Anybody(Permission):

    """Allow anybody access"""


class Nobody(Permission):

    """Deny everyone access"""


class Universals(RuleSet):

    rules = Items(
        allowAnybody = [Anybody],
        denyEverybody = [Nobody],
    )

    def allowAnybody(klass, attempt):
        return True

    def denyEverybody(klass, attempt):
        return False

Universals.declareRulesFor(IPermissionChecker)

















