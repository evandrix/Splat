"""PEAK Exceptions"""

class NamingException(Exception):

    """Base class for all peak.naming exceptions

        Supports the following constructor keyword arguments, which then
        become attributes of the exception object:

            rootException -- Exception that caused this exception to be thrown.

            rootTraceback -- Traceback of the root exception.

            resolvedName -- The portion of the name that was successfully
                resolved.

            resolvedObj -- The object through which resolution was successful,
                i.e., the object to which 'resolvedName' is bound.

            remainingName -- The remaining portion of the name which could not
                be resolved.

        The constructor also accepts an arbitrary number of unnamed arguments,
        which are treated the way arguments to the standard Exception class
        are treated.  (That is, saved in the 'args' attribute and used in the
        '__str__' method for formatting.)
    """

    formattables = ('resolvedName', 'remainingName', 'resolvedObj',)
    otherattrs   = ('rootTraceback', 'args', 'rootException',)

    __slots__ = list( formattables + otherattrs )


    def __init__(self, *args, **kw):

        for k in self.formattables+self.otherattrs:
            setattr(self,k,kw.get(k))

        self.args = args

    def __repr__(self):

        """Format the exception"""

        txt = Exception.__str__(self)

        extras = [
            '%s=%r' % (k,getattr(self,k))
            for k in self.formattables if getattr(self,k,None) is not None
        ]

        if extras:
            return "%s [%s]" % (txt, ','.join(extras))

        return txt


    def __str__(self):
        return `self`



class InvalidName(NamingException):
    """Unparseable string or non-name object"""


class NameNotFound(NamingException, LookupError):
    """A name could not be found"""


class NotAContext(NamingException):
    """Continuation is not a context/does not support required interface"""


class EnumerationError(KeyError,ValueError):
    """Invalid name or value for enumeration"""

class InvalidRoot(TypeError):
    """Root component doesn't support 'config.IConfigurationRoot'"""


# Config

class PropertyNotFound(NameNotFound):
    """DEPRECATED: Use 'NameNotFound' instead!"""


# Storage

class NotReadyError(Exception):
    """One or more transaction participants were unready too many times"""

class TransactionInProgress(Exception):
    """Action not permitted while transaction is in progress"""

class OutsideTransaction(Exception):
    """Action not permitted while transaction is not in progress"""

class BrokenTransaction(Exception):
    """Transaction can't commit, due to participants breaking contracts
       (E.g. by throwing an exception during the commit phase)"""


class TooManyResults(Exception):
    """Too many results were returned from a query

    (Either only one row was expected and there were multiple rows, or
    only one set of rows was expected and there were multiple sets."""


class TooFewResults(Exception):
    """Exactly one row was expected, but no rows were returned."""

# Running

class StopRunning(Exception):
    """Task doesn't want to be rescheduled"""





