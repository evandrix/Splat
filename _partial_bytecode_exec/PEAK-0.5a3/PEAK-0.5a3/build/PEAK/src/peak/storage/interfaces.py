"""'Straw Man' Transaction Interfaces"""

from protocols import Interface, Attribute, advise
from peak.binding.interfaces import IComponent
from peak.api import NOT_GIVEN

__all__ = [
    'ITransactionService', 'ITransactionParticipant', 'ICache',
    'ITransactionErrorHandler', 'ICursor', 'IRow',
    'IDataManager', 'IDataManager_SPI', 'IWritableDM', 'IWritableDM_SPI',
    'IManagedConnection', 'IManagedConn_SPI', 'IKeyableDM',
    'ISQLConnection', 'ILDAPConnection', 'IDDEConnection',
    'ISQLObjectLister'
]



























class ITransactionService(Interface):

    """Manages transaction lifecycle, participants, and metadata.

    There is no predefined number of transactions that may exist, or
    what they are associated with.  Depending on the application
    model, there may be one per application, one per transaction, one
    per incoming connection (in server applications), or some other
    number.  The transaction package should, however, offer an API for
    managing per-thread (or per-app, if threads aren't being used)
    transactions, since this will probably be the most common usage
    scenario."""

    # The basic transaction lifecycle

    def begin(**info):
        """Begin a transaction.  Raise TransactionInProgress if
        already begun.  Any keyword arguments are passed on to the
        setInfo() method.  (See below.)"""

    def commit():
        """Commit the transaction, or raise OutsideTransaction if not in
        progress."""

    def abort():
        """Abort the transaction, or raise OutsideTransaction if not in
        progress."""

    def fail():
        """Force transaction to fail (i.e. no commits allowed, only aborts)"""











    # Managing participants

    def join(participant):
        """Add 'participant' to the set of objects that will receive
        transaction messages.  Note that no particular ordering of
        participants should be assumed.  If the transaction is already
        active, 'participant' will receive a 'begin_txn()' message. If
        a commit or savepoint is in progress, 'participant' may also
        receive other messages to "catch it up" to the other
        participants.  However, if the commit or savepoint has already
        progressed too far for the new participant to join in, a
        TransactionInProgress error will be raised."""

    def __contains__(participant):
        """Has 'participant' joined?"""

    def removeParticipant(participant):
        """Force participant to be removed; for error handler use only"""

    # Getting/setting information about a transaction

    def isActive():
        """Return True if transaction is in progress."""

    def getTimestamp():
        """Return the time that the transaction began, in time.time()
        format, or None if no transaction in progress."""

    def addInfo(**info):
        """Update the transaction's metadata dictionary with the
        supplied keyword arguments.  This can be used to record
        information such as a description of the transaction, the user
        who performed it, etc. Note that the transaction itself does
        nothing with this information. Transaction participants will
        need to retrieve the information with 'getInfo()' and record
        it at the appropriate point during the transaction."""

    def getInfo():
        """Return a copy of the transaction's metadata dictionary"""


class ITransactionParticipant(Interface):

    """Participant in a transaction; may be a resource manager, a transactional
    cache, or just a logging/monitoring object.

    Event sequence is approximately as follows:

        join(participant)
            ( readyToVote voteForCommit commitTransaction ) | abortTransaction

    An abortTransaction may occur at *any* point following join(), and
    aborts the transaction.

    Generally speaking, participants fall into a few broad categories:

    * Database connections

    * Resource managers that write data to another participant, e.g. a
      storage manager writing to a database connection

    * Resource managers that manage their own storage transactions,
      e.g. ZODB Database/Storage objects, a filesystem-based queue, etc.

    * Objects which don't manage any transactional resources, but need to
      know what's happening with a transaction, in order to log it.

    Each kind of participant will typically use different messages to
    achieve their goals.  Resource managers that use other
    participants for storage, for example, won't care much about
    'voteForCommit()', while a resource manager that manages direct storage
    will care about 'voteForCommit()' very deeply!

    Resource managers that use other participants for storage, but
    buffer writes to the other participant, will need to pay close
    attention to the 'readyToVote()' message.  Specifically, they must
    flush all pending writes to the participant that handles their
    storage, and return 'False' if there was anything to flush.
    'readyToVote()' will be called repeatedly on *all* participants until
    they *all* return 'True', at which point the transaction will initiate
    the 'voteForCommit()' phase.

    By following this algorithm, any number of participants may be
    chained together, such as a persistence manager that writes to an
    XML document, which is persisted in a database table, which is
    persisted in a disk file.  The persistence manager, the XML
    document, the database table, and the disk file would all be
    participants, but only the disk file would actually use
    'voteForCommit()' and 'commitTransaction()' to handle a commit.
    All of the other participants would flush pending updates during the
    'readyToVote()' loop, guaranteeing that the disk file participant
    would know about all the updates by the time 'voteForCommit()' was
    issued, regardless of the order in which the participants received
    the messages."""

    def readyToVote(txnService):
        """Transaction commit is beginning; flush dirty objects and
        enter write-through mode, if applicable.  Return a true
        value if nothing needed to be done, or a false value if
        work needed to be done.  DB connections will probably never
        do anything here, and thus will just return a true value.
        Object managers like Entity DMs will write their objects and
        return false, or return true if they have nothing to write.
        Note: participants *must* continue to accept writes until
        'voteForCommit()' occurs, and *must* accept repeated writes
        of the same objects!"""

    def voteForCommit(txnService):
        """Raise an exception if commit isn't possible.  This will
        mostly be used by resource managers that handle their own
        storage, or the few DB connections that are capable of
        multi-phase commit."""

    def commitTransaction(txnService):
        """This message follows vote_commit, if no participants vetoed
        the commit.  DB connections will probably issue COMMIT TRAN
        here. Transactional caches might use this message to reset
        themselves."""





    def abortTransaction(txnService):
        """This message can be received at any time, and means the
        entire transaction must be rolled back.  Transactional caches
        might use this message to reset themselves."""

    def finishTransaction(txnService, committed):
        """The transaction is over, whether it aborted or committed."""


class ITransactionErrorHandler(Interface):

    """Policy object to handle exceptions issued by participants"""

    def voteFailed(txnService, participant):
        """'participant' raised exception during 'voteForCommit()'"""

    def abortFailed(txnService, participant):
        """'participant' raised exception during 'abortTransaction'"""

    def finishFailed(txnService, participant):
        """'participant' raised exception during 'finishTransaction()'"""

    def commitFailed(txnService, participant):
        """'participant' raised exception during 'commitTransaction()'"""

















# DM interfaces
from peak.persistence import IPersistentDataManager

class IDataManager(IComponent,ITransactionParticipant):

    """Data manager for persistent objects or queries"""

    resetStatesAfterTxn = Attribute(
        """Set to false to disable auto-deactivation of objects from cache"""
    )

    def __getitem__(oid):
        """Retrieve the persistent object designated by 'oid'"""

    def preloadState(oid, state):
        """Pre-load 'state' for object designated by 'oid' and return it"""


class IKeyableDM(IDataManager):

    """Data manager that supports "foreign key" references"""

    def oidFor(ob):
        """Return an 'oid' suitable for retrieving 'ob' from this DM"""


class IWritableDM(IKeyableDM):

    """Data manager that possibly supports adding/modifying objects"""

    advise(
        # Can't subclass this if it's a Zope Interface, but we can extend it:
        protocolExtends = [IPersistentDataManager]
    )

    def newItem(klass=None):
        """Create and return a new persistent object of class 'klass'"""

    def flush(ob=None):
        """Sync stored state to in-memory state of 'ob' or all objects"""

class IDataManager_SPI(Interface):

    """Methods/attrs that must/may be redefined in a QueryDM subclass"""

    cache = Attribute("a cache for ghosts and loaded objects")

    defaultClass = Attribute("Default class used for 'newItem()' method")

    def _ghost(oid, state=None):
        """Return a ghost of appropriate class, based on 'oid' and 'state'

        Note that 'state' will be loaded into the returned object via its
        '__setstate__()' method.  If 'state' is 'None', the returned object's
        '_p_deactivate()' method will be called instead."""


    def _load(oid, ob):
        """Load & return the state for 'oid', suitable for '__setstate__()'"""


class IWritableDM_SPI(IDataManager_SPI):

    """Additional methods needed for writing objects in an EntityDM"""

    def _save(ob):
        """Save 'ob' to underlying storage"""

    def _new(ob):
        """Create 'ob' in underlying storage and return its new 'oid'"""

    def _defaultState(ob):
        """Return a default '__setstate__()' state for a new 'ob'"""

    def _thunk(ob):
        """Hook for implementing cross-database "thunk" references"""






# Connection interfaces

class IManagedConnection(IComponent,ITransactionParticipant):

    """Transactable "Connection" object that appears to always be open"""

    connection = Attribute(

        """The actual underlying (LDAP, SQL, etc.) connection object

        This attribute is primarily for use by subclasses of ManagedConnection.
        It is a 'binding.Make()' link to the '_open()' method (see
        IManagedConnImpl interface for details)."""
    )

    txnTime = Attribute(
        """This connection's view of the Unix-format time of this transaction

        This attribute should be computed once and stored for the transaction
        duration, by something like 'SELECT GETDATE()' in the case of an SQL
        connection.  If the underlying connection has no notion of the current
        time, this can be computed by calling getTimestamp() on the transaction
        object.  In any event, accessing this attribute should ensure that the
        connection joins the current transaction, if it hasn't already"""
    )

    def joinTxn():
        """Join the current transaction, if not already joined"""

    def assertUntransacted():
        """Raise 'TransactionInProgress' if transaction already joined"""

    def closeASAP():
        """Close the connection as soon as it's not in a transaction"""

    def close():
        """Close the connection immediately"""




    def __call__(*args, **kw):
        """Return a (possibly initialized) ICursor

            Creates a new ICursor instance initialized with the passed
            keyword arguments.  If positional arguments are supplied,
            they are passed to the new cursor's 'execute()' method before
            it is returned.

            This method is the primary way of interacting with a connection;
            either you'll pass positional arguments and receive an
            initialized and iterable cursor, or you'll call with no arguments
            or keywords only to receive a cursor that you can use to perform
            more "low-level" interactions with the database.
        """


    def registerCursor(ob):
        """Register an object whose 'close()' method must be called"""


    def closeCursor():
        """Close all registered cursors which are still active"""



















# XXX These need more fleshing out w/API, exceptions, etc

class ISQLConnection(IManagedConnection):

    """A ManagedConnection that talks SQL"""

    def getRowConverter(description,post=None):
        """Get row-convert function for a given DBAPI description (or None)

        For the given 'description', which is a DBAPI cursor result description
        (i.e. sequence of tuples describing result columns), return a conversion
        function which will map the values in a row, to application-specific
        datatypes.  (The database-type to application-type mapping should be
        controlled via the connection's configuration properties.)

        The created conversion function will accept a single database result
        row, and return a sequence of values.  'post' is an optional
        postprocessing function which will be passed the entire sequence of
        converted values as a single argument.  The return value of 'post' will
        then be returned from the conversion function.

        Note that if no postprocessing function is supplied, and no columns in
        the given description require type conversion, this method may
        return 'None', indicating that no conversion of any kind is required.
        """

    DRIVER = Attribute(
        """The name of the DBAPI driver module for this connection"""
    )

    appConfig = Attribute(
        """A config.Namespace() pointing to 'DRIVER.appConfig'"""
    )

class ILDAPConnection(IManagedConnection):
    """A ManagedConnection that talks LDAP"""

class IDDEConnection(IManagedConnection):
    """A ManagedConnection that talks DDE"""


class IManagedConn_SPI(Interface):

    """Methods that must/may be defined in a ManagedConnection subclass"""

    def _open():
        """Return new "real" connection to be saved as 'self.connection'

            This method will be called whenever a new connection needs to
            be opened.  It should return an opened connection of the
            appropriate type, using whatever configuration data is
            available.  The result will be saved as 'self.connection' for
            use by other methods.  (Note: your subclass code shouldn't call
            'self._open()', since it'll be called automatically if it's
            needed, when you attempt to use 'self.connection'.

            Overriding this method is required.
        """

    def _close(self):
        """Actions to take before 'del self.connection', if needed.

            This method is automatically called when 'self.connection'
            exists and needs to be closed.  If your subclass needs to
            do anything special at this time (e.g. calling a close
            method on 'self.connection', you can override this method
            to do so.
        """














class ICache(Interface):

    """Cache - a restricted subset of the standard dictionary interface"""

    def get(key, default=None):
        """Retrieve object denoted by 'key', or 'default' if not found

            Note that cache implementations do not have to guarantee that
            'get()' will return items placed in the cache, or indeed
            ever return anything other than 'default'.  For example, the
            'NoCache' type always returns 'default'.
        """

    def __setitem__(key,value):
        """Save 'value' in the cache under 'key'

            Note that no particular lifetime for 'value' remaining in the
            cache is required.  For example, the 'NoCache' type implements
            this method as a no-op.
        """

    def clear():
        """Clear cache contents, if any"""


    def values():
        """Return a sequence of the cache's contents"""














class ICursor(Interface):

    """Iterable database cursor"""

    def execute(*args):

        """Execute a command

            Note that the types and semantics of this method's arguments
            are database-specific.  DBAPI cursors expect an SQL 'command'
            and an optional 'params' object, while LDAP cursors expect
            the arguments for an LDAP 'search' operation.

            Following 'execute()', a cursor should be ready for iteration
            over its result rows.
        """

    def __iter__():
        """Return an iterator returning the IRows of the result"""

    def allSets():
        """Return an iterator returning a list of IRows for each result set"""

    def justOne():
        """Assert that result contains only one IRow, and return it"""

    def __invert__():
        """The same as justOne(); i.e. '~cursor == cursor.justOne()'"""

    def nextset():
        """Result of calling the true DB cursor's 'nextset()', or None"""

    def close():
        """Close/reset the true DB cursor; the proxy can still be reused"""

    def dumpTo(stream, format=None, header=True, footer=True, delim='|', **kw):
        """render cursor to stream"""


class IRow(Interface):
    """Row that smells like a tuple, dict, or instance attr"""



class ISQLObjectLister(Interface):
    """Adapt a managed connection to this to obtain information on
       objects in the database"""

    def listObjects(full=False, obtypes=NOT_GIVEN):
        """Returns an active cursor with information on objects in the DB

            with full=True, includes all available information, otherwise
            only includes the information likely to be most elevant to the
            user.

            The returned cursor shall have a column 'obname' first, with
            the object name, and a column 'obtype' second, with one of
            the following values standardized:

                table, systable, view, proc, index, synonym

            if obtypes is given, it shall be a sequence of the above types,
            and rows shall only be returned for the given types.
        """





















