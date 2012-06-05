from peak.api import *
from interfaces import *
from time import time


__all__ = [
    'TransactionService', 'AbstractParticipant', 'TransactionComponent',
    'BasicTxnErrorHandler', 'getTransaction', 'beginTransaction',
    'commitTransaction', 'abortTransaction', 'begin', 'commit', 'abort',
]


def getTransaction(subject):
    return config.lookup(subject,ITransactionService)

def beginTransaction(subject, **info):
    getTransaction(subject).begin(**info)

def commitTransaction(subject):
    getTransaction(subject).commit()

def abortTransaction(subject):
    getTransaction(subject).abort()


begin  = beginTransaction
commit = commitTransaction
abort  = abortTransaction













class BasicTxnErrorHandler(object):

    """Simple error handling policy, w/simple logging, no retries"""

    protocols.advise(
        instancesProvide=[ITransactionErrorHandler]
    )

    def voteFailed(self, txnService, participant):

        txnService.logger.warning(
            "%s: error during participant vote", txnService, exc_info=True
        )

        # Force txn to abort
        txnService.fail()
        raise


    def commitFailed(self, txnService, participant):

        txnService.logger.critical(
            "%s: unrecoverable transaction failure", txnService,
            exc_info=True
        )
        txnService.fail()
        raise


    def abortFailed(self, txnService, participant):

        txnService.logger.warning(
            "%s: error during participant abort", txnService,
            exc_info=True
        )

        # ignore the error




    def finishFailed(self, txnService, participant, committed):

        txnService.logger.warning(
            "%s: error during participant finishTransaction", txnService,
            exc_info=True
        )

        # ignore the error

































class TransactionState(binding.Component):

    """Helper object representing a single transaction's state"""

    participants = binding.Make(list)
    info         = binding.Make(dict)
    timestamp    = None
    safeToJoin   = True
    cantCommit   = False



class TransactionService(binding.Component):

    """Basic transaction service component"""

    protocols.advise(
        instancesProvide=[ITransactionService]
    )

    state          = binding.Make(TransactionState)
    errorHandler   = binding.Make(BasicTxnErrorHandler)
    logger         = binding.Obtain(PropertyName('peak.logs.transaction'))

    def join(self, participant):

        if self.state.cantCommit:
            raise exceptions.BrokenTransaction

        elif not self.isActive():
            raise exceptions.OutsideTransaction

        elif self.state.safeToJoin:

            if participant not in self.state.participants:
                self.state.participants.append(participant)

        else:
            raise exceptions.TransactionInProgress


    def _prepare(self):

        """Get votes from all participants

        Ask all participants if they're ready to vote, up to N+1 times (where
        N is the number of participants), until all agree they are ready, or
        an exception occurs.  N+1 iterations is sufficient for any acyclic
        structure of cascading data managers.  Any more than that, and either
        there's a cascade cycle or a broken participant is always returning a
        false value from its readyToVote() method.

        Once all participants are ready, ask them all to vote."""

        tries = 0
        unready = True
        state = self.state

        while unready and tries <= len(state.participants):
            unready = [p for p in state.participants if not p.readyToVote(self)]
            tries += 1

        if unready:
            raise exceptions.NotReadyError(unready)


        self.state.safeToJoin = False

        for p in state.participants:
            try:
                p.voteForCommit(self)
            except:
                self.errorHandler.voteFailed(self,p)

        return True







    def begin(self, **info):

        if self.isActive():
            raise exceptions.TransactionInProgress

        self.state.timestamp = time()
        self.addInfo(**info)


    def commit(self):

        if not self.isActive():
            raise exceptions.OutsideTransaction

        if self.state.cantCommit:
            raise exceptions.BrokenTransaction

        self._prepare()

        for p in self.state.participants:
            try:
                p.commitTransaction(self)
            except:
                self.errorHandler.commitFailed(self,p)

        self._cleanup(True)


    def fail(self):

        if not self.isActive():
            raise exceptions.OutsideTransaction

        self.state.cantCommit = True
        self.state.safeToJoin = False


    def removeParticipant(self,participant):
        self.state.participants.remove(participant)


    def abort(self):

        if not self.isActive():
            raise exceptions.OutsideTransaction

        self.fail()

        for p in self.state.participants[:]:
            try:
                p.abortTransaction(self)
            except:
                self.errorHandler.abortFailed(self,p)

        self._cleanup(False)


    def getTimestamp(self):

        """Return the time that the transaction began, in time.time()
        format, or None if no transaction in progress."""

        return self.state.timestamp


    def addInfo(self, **info):

        if self.state.cantCommit:
            raise exceptions.BrokenTransaction

        elif self.state.safeToJoin:
            self.state.info.update(info)

        else:
            raise exceptions.TransactionInProgress



    def getInfo(self):
        return self.state.info


    def _cleanup(self, committed):

        for p in self.state.participants[:]:
            try:
                p.finishTransaction(self,committed)
            except:
                self.errorHandler.finishFailed(self,p,committed)

        del self.state


    def isActive(self):
        return self.state.timestamp is not None


    def __contains__(self,ob):
        return ob in self.state.participants
























class AbstractParticipant(object):

    protocols.advise(
        instancesProvide = [ITransactionParticipant]
    )

    def readyToVote(self, txnService):
        return True

    def voteForCommit(self, txnService):
        pass

    def commitTransaction(self, txnService):
        pass

    def abortTransaction(self, txnService):
        pass

    def finishTransaction(self, txnService, committed):
        pass





















class TransactionComponent(binding.Component, AbstractParticipant):

    """Object that has a 'txnSvc' and auto-joins transactions"""

    inTransaction = False

    txnAttrs = 'joinedTxn', 'inTransaction'

    def joinedTxn(self,instDict,attrName):

        """Our TransactionService (auto-joined when attribute is accessed)"""

        ts = self.txnSvc
        ts.join(self)
        self.inTransaction = True
        instDict[attrName] = ts
        self.onJoinTxn(ts)
        return ts

    joinedTxn = binding.Make(joinedTxn)

    txnSvc = binding.Obtain(ITransactionService,offerAs=[ITransactionService])

    def onJoinTxn(self, txnService):
        pass

    def finishTransaction(self, txnService, committed):

        """Ensure that subsequent transactions will require re-registering"""

        d = self.__dict__
        have = d.has_key

        for attr in self.txnAttrs:
            if have(attr):
                del d[attr]





