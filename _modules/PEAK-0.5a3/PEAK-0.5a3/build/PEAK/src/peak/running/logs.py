'''TODO:

    * Flesh out ILogEvent, docs

    * SysLog and LogTee objects/URLs (low priority; we don't seem to use
      these at the moment)
'''

from peak.naming import URL
from peak.api import *
from peak.naming.factories.openable import FileURL
from peak.naming.interfaces import IObjectFactory
from peak.util.imports import whenImported
from time import time, localtime, strftime
import sys, os, traceback

from socket import gethostname
_hostname = gethostname().split('.')[0]
del gethostname


__all__ = [
    'AbstractLogger', 'LogFile', 'LogStream', 'DefaultLoggingService',
    'IBasicLogger', 'ILogger', 'ILogEvent', 'ILoggingService',
]
















class IBasicLogger(protocols.Interface):

    """A PEP 282 "logger" object, minus configuration methods

    All methods that take 'msg' and positional arguments 'args' will
     interpolate 'args' into 'msg', so the format is a little like a
    'printf' in C.  For example, in this code:

        aLogger.debug("color=%s; number=%d", "blue", 42)

    the log message will be rendered as '"color=blue; number=42"'.  Loggers
    should not interpolate the message until they have verified that the
    message will not be trivially suppressed.  (For example, if the logger
    is not accepting messages of the designated priority level.)  This avoids
    needless string processing in code that does a lot of logging calls that
    are mostly suppressed.  (E.g. debug logging.)

    Methods that take a '**kwargs' keywords argument only accept an 'exc_info'
    flag as a keyword argument.  If 'exc_info' is a true value, exception data
    from 'sys.exc_info()' is added to the log message.
    """

    def isEnabledFor(lvl):
        """Return true if logger will accept messages of level 'lvl'"""

    def getEffectiveLevel():
        """Get minimum priority level required for messages to be accepted"""

    def debug(msg, *args, **kwargs):
        """Log 'msg' w/level DEBUG"""

    def info(msg, *args, **kwargs):
        """Log 'msg' w/level INFO"""

    def warning(msg, *args, **kwargs):
        """Log 'msg' w/level WARNING"""

    def error(msg, *args, **kwargs):
        """Log 'msg' w/level ERROR"""


    def critical(msg, *args, **kwargs):
        """Log 'msg' w/level CRITICAL"""

    def exception(msg, *args):
        """Log 'msg' w/level ERROR, add exception info"""

    def log(lvl, msg, *args, **kwargs):
        """Log 'msg' w/level 'lvl'"""


class ILogger(IBasicLogger):

    """A PEAK logger, with additional (syslog-compatible) level methods"""

    def trace(msg, *args, **kwargs):
        """Log 'msg' w/level TRACE"""

    def notice(msg, *args, **kwargs):
        """Log 'msg' w/level NOTICE"""

    def alert(msg, *args, **kwargs):
        """Log 'msg' w/level ALERT"""

    def emergency(msg, *args, **kwargs):
        """Log 'msg' w/level EMERG"""


class ILogEvent(protocols.Interface):
    """Temporary marker to allow configurable event classes

    This interface will be fleshed out more later, as the log system
    syncs up more with the capabilities and interfaces of the Python
    2.3 logging package.
    """







class ILoggingService(protocols.Interface):

    """A service that supplies loggers"""

    def getLogger(name=''):
        """Get an ILogger for 'name'"""

    def getLevelName(lvl, default=NOT_GIVEN):

        """Get a name for integer 'lvl', or return 'default'

        If 'lvl' is not a recognized level, and 'default' is not given,
        return 'str(lvl)'."""

    def getLevelFor(ob, default=NOT_GIVEN):

        """Get a level integer for 'ob', or return 'default'

        If 'ob' is in fact a number (i.e. adding 0 to it works), return as-is.
        If 'ob' is a string representation of an integer, return numeric value,
        so that functions which want to accept either numbers or level names
        can do so by calling this converter.

        If no conversion can be found, and no default is specified, raise
        LookupError."""
















class DefaultLoggingService(binding.Component):

    """Service that supplies loggers"""

    protocols.advise(
        instancesProvide=[ILoggingService]
    )

    loggerNS  = binding.Make(config.Namespace('peak.logs'))
    levelsNS  = binding.Make(config.Namespace('peak.logging.levels'))
    loggers   = binding.Make(dict)

    def nameForLevel(self):
        names = {}
        for k in config.iterKeys(self,'peak.logging.levels'):
            if k.endswith('?'):
                continue    # Don't use ?-tagged rules to create values
            k = k.split('.')[-1]; names[self.levelsNS[k]] = k
        return names

    nameForLevel = binding.Make(nameForLevel)


    def getLogger(self, name=''):
        """Get an ILogger for 'name'"""

        if name<>'':
            name = PropertyName(name)
            if not name.isPlain():
                raise exceptions.InvalidName(
                    "%r is not a plain property name" % name
                )

        try:
            return self.loggers[name]
        except KeyError:
            logger = self.loggers[name] = self.loggerNS[name]
            binding.suggestParentComponent(self,name,logger)
            return logger


    def getLevelName(self, lvl, default=NOT_GIVEN):

        """Get a name for 'lvl', or return 'default'

        If 'default' is not given, return '"Level %s" % lvl', for
        symmetry with the 'logging' package."""

        try:
            return self.nameForLevel[lvl]
        except KeyError:
            pass

        if default is NOT_GIVEN:
            return str(lvl)

        return default

























    def getLevelFor(self, ob, default=NOT_GIVEN):

        """Get a level integer for 'ob', or return 'default'

        If 'ob' is in fact a number (i.e. adding 0 to it works), return as-is.
        If 'ob' is a string representation of an integer, return numeric value,
        so that functions which want to accept either numbers or level names
        can do so by calling this converter.

        If no conversion can be found, and no default is specified, raise
        LookupError."""

        try:
            return ob+0     # If this works, it's a number, leave it alone
        except TypeError:
            pass

        try:
            return self.levelsNS[ob]
        except KeyError:
            pass

        try:
            # See if we can convert it to a number
            return int(ob)
        except ValueError:
            pass

        if default is NOT_GIVEN:
            raise LookupError("No such log level", ob)

        return default









whenImported('logging',
    lambda logging: (
        # Add the other syslog levels
        logging.addLevelName(25, 'NOTICE'),
        logging.addLevelName(60, 'ALERT'),
        logging.addLevelName(70, 'EMERG'),

        # And make it so PEP 282 loggers can be adapted to ILogger
        protocols.declareImplementation(
            logging.getLogger().__class__,
            instancesProvide = [IBasicLogger]
        )
    )
)


# DEPRECATED LEVEL CONSTANTS -- do not use, they vanish in a4!
nms  = 'TRACE ALL DEBUG INFO NOTICE WARNING ERROR CRITICAL ALERT EMERG'.split()
lvls =      0,  0,   10,  20,    25,     30,   40,      50,   60,   70
globals().update(dict(zip(nms,lvls)))





















class Event(binding.Component):

    ident      = 'PEAK' # XXX use component names if avail?
    msg        = ''
    args       = ()
    priority   = binding.Require("Integer priority level")
    timestamp  = binding.Make(lambda: time())
    uuid       = binding.Make('peak.util.uuid:UUID')
    hostname   = _hostname
    process_id = binding.Make(lambda: os.getpid())
    message    = binding.Make(
        lambda self: self.args and (self.msg % self.args) or self.msg
    )
    exc_info   = ()

    def traceback(self,d,a):
        if self.exc_info:
            return ''.join(traceback.format_exception(*self.exc_info))
        return ''

    traceback = binding.Make(traceback)

    def __init__(self, parentComponent=NOT_GIVEN, componentName=None, **info):
        super(Event,self).__init__(parentComponent,componentName,**info)
        if not isinstance(self.exc_info, tuple):
            self.exc_info = sys.exc_info()

    def keys(self):
        return [k for k in self.__dict__.keys() if not k.startswith('_')]

    def items(self):
        return [
            (k,v) for k,v in self.__dict__.items() if not k.startswith('_')
        ]

    def __contains__(self, key):
        return not key.startswith('_') and key in self.__dict__

    def __getitem__(self, key):
        return getattr(self,key)

    def linePrefix(self):
        return  "%s %s %s[%d]: " % (
            strftime('%b %d %H:%M:%S', localtime(self.timestamp)),
            _hostname, self.ident, self.process_id
        )

    linePrefix = binding.Make(linePrefix)


    def asString(self):

        if self.exc_info:
            return '\n'.join(filter(None,[self.message,self.traceback]))
        else:
            return self.message

    asString = binding.Make(asString)


    def prefixedString(self):
        return '%s%s\n' % (
            self.linePrefix,
            self.asString.rstrip().replace('\n', '\n'+self.linePrefix)
        )

    prefixedString = binding.Make(prefixedString)


    def __unicode__(self):
        return self.prefixedString


    def __str__(self):
        return self.prefixedString.encode('utf8','replace')







class logfileURL(FileURL):

    supportedSchemes = ('logfile', )
    defaultFactory = 'peak.running.logs.LogFile'

    class level(URL.Field):
        defaultValue = 'ALL'

    querySyntax = URL.Sequence('level=', level)


class peakLoggerURL(URL.Base):

    """URL that only looks up PEAK loggers, even if 'logging' is installed"""

    supportedSchemes = ('logging.logger', 'logger')

    def getCanonicalBody(self):
        if self.body<>'':
            body = PropertyName(self.body)
            if not body.isPlain():
                raise exceptions.InvalidName(
                    "%r is not a plain property name in logger: URL" % body
                )
            return body
        return self.body


class peakLoggerContext(naming.AddressContext):

    schemeParser = peakLoggerURL
    logSvc       = binding.Obtain(ILoggingService)

    def _get(self, name, retrieve=1):
        return self.logSvc.getLogger(name.body)






def _levelledMessage(lvl):

    lvlName = lvl.lower()

    meth = \
     """def %(lvlName)s(self, msg, *args, **kwargs):
            if self.level <= self.%(lvl)s:
                self.publish(
                    self.EventClass(
                        self, msg=msg, args=args, priority=self.%(lvl)s,
                        ident=self.logName, **kwargs
                    )
                )
""" % locals()

    d = {}
    exec meth in d

    return d[lvlName]






















class AbstractLogger(binding.Component):

    protocols.advise(
        instancesProvide=[ILogger]
    )

    logSvc = binding.Obtain(ILoggingService)
    levelName = binding.Require("Minimum priority for messages to be published")
    level = binding.Make(lambda self: self.logSvc.getLevelFor(self.levelName))
    EventClass = binding.Obtain(config.FactoryFor(ILogEvent))
    logName = binding.Make(lambda self: self.getComponentName())

    def isEnabledFor(self,lvl):
        return self.level <= lvl

    def getEffectiveLevel(self):
        return self.level

    TRACE = DEBUG = INFO = NOTICE = WARNING = ERROR = CRITICAL = \
        ALERT = EMERG = \
            binding.Make(lambda self,d,a: self.logSvc.getLevelFor(a))

    trace     = _levelledMessage('TRACE')
    debug     = _levelledMessage('DEBUG')
    info      = _levelledMessage('INFO')
    notice    = _levelledMessage('NOTICE')
    warning   = _levelledMessage('WARNING')
    error     = _levelledMessage('ERROR')
    critical  = _levelledMessage('CRITICAL')
    alert     = _levelledMessage('ALERT')
    emergency = _levelledMessage('EMERG')

    def exception(self, msg, *args, **kwargs):
        if self.level <= self.ERROR:
            self.publish(
                self.EventClass(
                    self, msg=msg, args=args, priority=ERROR,
                    exc_info=True, ident=self.logName, **kwargs
                )
            )

    def log(self, lvl, msg, *args, **kwargs):
        if self.level <= lvl:
            self.publish(
                self.EventClass(
                    self, msg=msg, args=args, priority=lvl, ident=self.logName,
                    **kwargs
                )
            )

    def publish(self, event):
        pass

    def __call__(self, priority, msg, ident=None):

        # XXX backward-compatibility w/AppUtils
        # XXX do we need this?

        if priority>=self.level:
            if isinstance(msg,tuple):
                e = Event('ERROR', exc_info = msg)
            else:
                e = Event(msg, priority=priority)

            if ident is not None:
                e.ident = ident

        self.sink(e)














class LogFile(AbstractLogger):

    filename = binding.Require("name of file to write logs to")
    protocols.advise(classProvides=[IObjectFactory])

    def publish(self, event):
        if event.priority >= self.level:
            fp = open(self.filename, "a")
            try:
                fp.write(str(event))
            finally:
                fp.close()

    def getObjectInstance(klass, context, refInfo, name, attrs=None):
        url, = refInfo.addresses
        logSvc = config.lookup(context,ILoggingService)
        level  = logSvc.getLevelFor(
            url.level.upper()[
                (url.level.upper()[:4] in ('PRI_','LOG_') and 4 or 0):
            ]
        )
        return klass(filename=url.getFilename(), level=level)

    getObjectInstance = classmethod(getObjectInstance)


class LogStream(AbstractLogger):

    stream = binding.Require("Writable stream to write messages to")

    def publish(self, event):
        if event.priority >= self.level:
            self.stream.write(str(event))








