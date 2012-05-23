"""Test log services

    TODO:

        * Test formatting, AppUtils-style __call__, ...?

        * Test exception/traceback support

"""

from unittest import TestCase, makeSuite, TestSuite
from peak.api import *
from peak.tests import testRoot

class TestLogger(logs.AbstractLogger):

    events = binding.Make(list)

    def publish(self,event):
        self.events.append(
            (
                event.ident,
                self.logSvc.getLevelName(event.priority), event.message,
            )
        )
















class TestApp(binding.Component):

    logSvc = binding.Make(
        'peak.running.logs:DefaultLoggingService',
        offerAs=[logs.ILoggingService]
    )

    foobar = binding.Make(
        lambda: -42,
        offerAs=['peak.logging.levels.FOO','peak.logging.levels.BAR?']
    )

    baz = binding.Make(lambda: 17, offerAs=['peak.logging.levels.BAZ'])
    spam = binding.Make(lambda: 91, offerAs=['peak.logging.levels.SPAM'])

    parseURL = naming.parseURL

    logger1 = binding.Make(
        lambda: TestLogger(levelName='ALL'),
        offerAs=['peak.logs.test1'], suggestParent=False
    )

    logger2 = binding.Make(
        lambda: TestLogger(level=30), # WARNING
        offerAs=['peak.logs.test2'], suggestParent=False
    )

    levels = binding.Make(config.Namespace('peak.logging.levels'))













class ServiceTests(TestCase):

    stdLevels  = 'TRACE DEBUG INFO NOTICE WARNING ERROR CRITICAL ALERT EMERG'
    stdNums    =      0,   10,  20,    25,     30,   40,      50,   60,   70
    stdMethods = (stdLevels + 'ENCY').lower().split()
    stdLevels  = (stdLevels+' ALL').split()
    stdNums    = stdNums + (0,)

    def setUp(self):
        self.app = TestApp(testRoot())
        self.getLogger = self.app.logSvc.getLogger
        self.getLevelFor = self.app.logSvc.getLevelFor
        self.getLevelName = self.app.logSvc.getLevelName
        #self.addListener = self.app.logSvc.addListener

    def doMessages(self,name,expectLevel,interp=False,useLog=False):

        logger = self.getLogger(name)
        expected = []

        self.assertEqual(logger.getEffectiveLevel(), expectLevel)

        for methodName,lvl,num in zip(self.stdMethods,self.stdLevels,self.stdNums):
            if useLog:
                meth = lambda *args,**kw: logger.log(num,*args,**kw)
            else:
                meth = getattr(logger,methodName)
            if interp:
                meth(methodName+" %s", lvl)
                if logger.isEnabledFor(num):
                    expected.append( (name,lvl,(methodName+" %s") % lvl) )
            else:
                meth(methodName)
                if logger.isEnabledFor(num):
                    expected.append( (name,lvl,methodName) )

            if num >= expectLevel:
                self.failUnless( logger.isEnabledFor(num) )

        self.assertEqual(logger.events, expected)

    def testBasicGets(self):

        self.failUnless(
            adapt(self.app.logSvc, logs.ILoggingService, None) is not None
        )

        logger1 = self.getLogger('test1')
        self.failUnless( adapt(logger1, logs.ILogger, None) is not None )

        logger2 = self.getLogger('test2')
        self.failUnless( adapt(logger2, logs.ILogger, None) is not None )

        # same timers for same names
        self.failUnless(logger1 is self.getLogger('test1'))
        self.failUnless(logger2 is self.getLogger('test2'))

        # different timers for different names
        self.failIf(logger1 is logger2)


    def testBuiltinLevels(self):
        for n,l in zip(self.stdLevels,self.stdNums):
            self.assertEqual(self.getLevelFor(n), l)
            if n<>'ALL':
                self.assertEqual(self.getLevelName(l), n)


    def testCustomLevels(self):
        nms = 'FOO BAR BAZ SPAM'
        lvls = -42,-42, 17,  91
        nms = nms.split()
        for n,l in zip(nms,lvls):
            self.assertEqual(self.getLevelFor(n), l)
            if n<>'BAR':
                self.assertEqual(self.getLevelName(l), n)






    def testInvalidLoggerNames(self):

        # verify that we get invalid name errors for invalid names, anywhere

        invalid = exceptions.InvalidName
        self.assertRaises(invalid, self.getLogger, 'foo bar')
        self.assertRaises(invalid, self.getLogger, 'foo?')
        self.assertRaises(invalid, self.getLogger, 'foo.*')

        #l = lambda *args: None
        #self.assertRaises(invalid, self.addListener,'foo bar',l)
        #self.assertRaises(invalid, self.addListener,'foo?', l)

        self.assertRaises(invalid, self.app.parseURL, 'logger:foo.*')
        self.assertRaises(invalid, self.app.parseURL, 'logger:foo bar')
        self.assertRaises(invalid, self.app.parseURL, 'logger:foo?')


    def testSimpleEvents(self):
        self.doMessages('test1',0,interp=False)
        self.doMessages('test2',30,interp=True)


    def testIndirectEvents(self):
        self.doMessages('test1',0,interp=False,useLog=True)
        self.doMessages('test2',30,interp=True,useLog=True)















TestClasses = (
    ServiceTests,
)

def test_suite():
    s = []
    for t in TestClasses:
        s.append(makeSuite(t,'test'))

    return TestSuite(s)































