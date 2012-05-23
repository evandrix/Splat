"""Support for atomic but "in a parallel transaction" operations"""

from peak.api import *
from peak.util.advice import advice

__all__ = [
    'AutoCommitter', 'Untransactable', 'autocommitted'
]


class AutoCommitter(storage.TransactionComponent):

    """TransactionComponent that supports 'autocommit' setting and methods

        'AutoCommitter' instances accept an 'autocommit' keyword argument
        which tells them they have permission to take control of their
        transaction boundaries.  Any 'autocommitted' methods of an
        'AutoCommitter' will automatically be wrapped in a transaction if
        the object has not already joined one.

        In addition, if a 'txnSvc' keyword isn't supplied, but 'autocommit'
        is a true value, 'AutoCommitter' objects allocate their own private
        transaction service instance, for use in 'autocommitted' methods.
        This transaction service will be shared with any sub-components of
        the 'AutoCommitter', thus ensuring composability.  You will normally
        want your subcomponents, however, to be created with a false or missing
        'autocommit' setting, so that they simply participate in your
        component's private transaction if appropriate.
    """

    autocommit = False

    def __init__(self,*__args,**__kw):

        super(AutoCommitter,self).__init__(self,*__args,**__kw)

        if self.autocommit and not self._hasBinding('txnSvc'):
            self.txnSvc = storage.TransactionService(self,'txnSvc')



class Untransactable(binding.Component):

    """Untransactable object that *requires* a true setting for 'autocommit'

        Subclass this if you have an object which is not transactional, but
        might be used interchangeably with similar 'AutoCommitter' objects.
        This ensures that an attempt to create an instance of your class
        will raise an exception if a true setting for 'autocommit' isn't
        supplied, thus warning the caller in the event that they mistakenly
        used the wrong implementation for their desired semantics.  For
        example, if they used an SMTP messaging class instead of a queue-based
        messaging class, but wanted the message send to wait until transaction
        commit time.
    """

    def __init__(self,*__args,**__kw):

        super(Untransactable,self).__init__(self,*__args,**__kw)

        if not self.autocommit:
            raise exceptions.TransactionsNotSupported(
                "%r does not support transactions; the 'autocommit'"
                " flag is required." % self
            )

















class autocommitted(advice):

    """meth = autocommited(meth) - Wrap a method with autocommit support

    'AutoCommitter' classes should wrap any methods which want to be
    atomic operations in an 'autocommitted()' advice.  For example::

        from peak.storage.autocommit import *

        class QueuedMessageSender(AutoCommitter):

            def send(self,message):
                # ...

            send = autocommitted(send)

    When a 'QueuedMessageSender' object's 'send()' method is called,
    it will be wrapped in a transaction as long as the object was
    created with a true setting for its 'autocommit' parameter.  If
    an error is raised from 'send()', the transaction will be aborted,
    otherwise it will be committed.

    If a wrapped method is called from inside another 'autocommitted()'
    method of the same object, or if the object doesn't have 'autocommit'
    set to a true value, no special transaction handling occurs.

    Note that errors raised during the wrapping transaction's commit or
    abort method may leave the object's transaction service stuck in a
    failure mode, where it cannot be committed, only aborted.  This can
    be fixed by calling the 'theBrokenObject.txnSvc.abort()' until it
    no longer raises an exception.  Or, it may be more worthwhile to
    set up a custom error handler on the transaction service instance
    used for autocommit transactions.  Once we have enough experience
    with this issue to know what's most useful, we may add such an
    error handler to the 'AutoCommitter' default 'txnSvc' setup code.

    Also note that wrapped methods should always use 'self.joinedTxn' to
    ensure they have joined a transaction; this wrapper doesn't do it for
    you.  (It can't, since it would then fail to work correctly when
    autocommit is turned off.)"""

    __slots__ = ()


    def __call__(__advice, self, *__args, **__kw):

        if self.autocommit and not self.txnSvc.isActive():

            # We only want to do this if a transaction isn't already in
            # progress, *and* the object is in autocommit mode.

            self.txnSvc.begin()

            try:
                retval = __advice._func(self, *__args, **__kw)
            except:
                self.txnSvc.abort()
                raise
            else:
                self.txnSvc.commit()
                return retval

        else:
            # Just call the method
            return __advice._func(self, *__args, **__kw)

















