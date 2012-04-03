from unittest import TestCase, makeSuite, TestSuite
from peak.api import *
from peak.tests import testRoot
from peak.running.tests import TestClock
from peak.running import timers


class TestApp(binding.Component):

    log = binding.Require("function to call with event data")
    testClock = binding.Make(lambda self:TestClock(log=self.log))

    run = sleep = binding.Delegate('testClock')

    time = binding.Obtain('testClock/time',
        offerAs=['peak.running.timers.elapsed']
    )

    clock = binding.Obtain('testClock/clock',
        offerAs=['peak.running.timers.cpu']
    )

    timerSvc = binding.Make(
        'peak.running.timers:TimerService', offerAs=[timers.ITimerService]
    )

    parseURL = naming.parseURL














class ServiceTests(TestCase):

    def setUp(self):
        self.log = []
        self.expectedLog = []
        self.app = TestApp(testRoot(), log = [].append)
        self.getTimer = self.app.timerSvc.getTimer
        self.addListener = self.app.timerSvc.addListener

    def tearDown(self):
        self.assertEqual(self.log, self.expectedLog)


    def testBasicGets(self):

        self.failUnless(
            adapt(self.app.timerSvc, timers.ITimerService, None) is not None
        )

        timer1 = self.getTimer('test1')
        self.failUnless( adapt(timer1, timers.ITimer, None) is not None )

        timer2 = self.getTimer('test2')
        self.failUnless( adapt(timer2, timers.ITimer, None) is not None )

        # same timers for same names
        self.failUnless(timer1 is self.getTimer('test1'))
        self.failUnless(timer2 is self.getTimer('test2'))

        # different timers for different names
        self.failIf(timer1 is timer2)










    def testInvalidTimerNames(self):

        # verify that we get invalid name errors for invalid names, anywhere

        invalid = exceptions.InvalidName
        self.assertRaises(invalid, self.getTimer, 'foo bar')
        self.assertRaises(invalid, self.getTimer, 'foo?')
        self.assertRaises(invalid, self.getTimer, 'foo.*')

        l = lambda *args: None
        self.assertRaises(invalid, self.addListener,'foo bar',l)
        self.assertRaises(invalid, self.addListener,'foo?', l)

        self.assertRaises(invalid, self.app.parseURL, 'timer:foo.*')
        self.assertRaises(invalid, self.app.parseURL, 'timer:foo bar')
        self.assertRaises(invalid, self.app.parseURL, 'timer:foo?')
        self.assertRaises(invalid, self.app.parseURL, 'timer:')
























    def testBasicTimerEvents(self):

        # This test sequence verifies:
        # * multiple listeners per timer and per event
        # * various event lists per timer
        # * info is set by start() and updated by resume(), addInfo(), & stop()
        # * resume() events get an intermediate snapshot of accumulated time
        # * resumed timers have correct time (for 1 resumption)
        # * notifications occur outside the measured time period
        # * listeners are called in the order they're added (XXX bad?)
        # * time measurements are correct, and only given by stop/resume calls

        cases = [
            ('test.1', {'foo':'bar'}, ['start','stop'],         1,0),
            ('test.2', {'spam':'baz'},['stop','resume','start'],1,1),
            ('test.3', {},            ['addInfo','stop'],       2,2),
        ]

        def expect(ev,info,elapsed=None,cpu=None):
            self.expectedLog.append((self.app.timerSvc,key,ev,info,elapsed,cpu))

        for key,d,ev,elapsed,cpu in cases:

            timer = self.getTimer(key)

            timer.addListener(
                lambda *args: self.app.run(10), ['start','stop','resume']
            )

            timer.addListener(
                lambda s,k,e,d,el=None,cp=None: self.log.append((s,k,e,d,el,cp)),
                ev
            )

            timer.start(**d)
            if 'start' in ev:
                expect('start',d)

            self.app.run(cpu)
            self.app.sleep(elapsed-cpu);

            if 'addInfo' in ev:
                d = d.copy(); d['extra']=42
                timer.addInfo(extra=42)
                expect('addInfo',d)

            timer.stop(stopped=key)
            d = d.copy(); d['stopped']=key

            if 'stop' in ev:
                expect('stop',d,elapsed,cpu)

            if 'resume' in ev:

                d = d.copy(); d['resumed']=key
                expect('resume',d,elapsed,cpu)

                timer.resume(resumed=key)
                self.app.sleep(cpu)
                timer.stop()

                if 'stop' in ev:
                    expect('stop',d,elapsed+cpu,cpu)



















    def listener(self,service,key,event,info,elapsed=None,processor=None):
        self.log.append((event,info,elapsed,processor))

    def expect(self,event,info,elapsed=None,processor=None):
        self.expectedLog.append((event,info,elapsed,processor))

    def verifyTimerStateMachine(self, timer):

        # Verify that only allowed invocation sequences are:
        #   reset* -> start/resume -> addInfo* -> stop -> ...

        # Or more simply, reset/start/resume can only happen when stopped,
        # and addInfo/stop can only occur while running.  Using any method
        # out of order should result in a TimerStateError.

        # This test also verifies that a listener with a wildcard ('None')
        # event mask receives all events, and that reset and resume work
        # correctly w/respect to timing and information recorded.

        expect = self.expect

        self.assertRaises(timers.TimerStateError, timer.stop)
        self.assertRaises(timers.TimerStateError, timer.addInfo)

        timer.start(started=1)
        expect('start',{'started':1})
        self.app.run(5)

        self.assertRaises(timers.TimerStateError, timer.start)
        self.assertRaises(timers.TimerStateError, timer.reset)
        self.assertRaises(timers.TimerStateError, timer.resume)

        timer.addInfo(addInfo=2)
        expect('addInfo',{'started':1, 'addInfo':2})
        timer.stop(stopped=3)
        expect('stop',{'started':1, 'addInfo':2, 'stopped':3},5,5)

        self.assertRaises(timers.TimerStateError, timer.stop)
        self.assertRaises(timers.TimerStateError, timer.addInfo)


        timer.reset()
        expect('reset',{})

        self.assertRaises(timers.TimerStateError, timer.stop)
        self.assertRaises(timers.TimerStateError, timer.addInfo)

        timer.resume(resume=4)
        expect('resume',{'resume':4},0,0)

        self.app.sleep(7)
        self.app.run(2)

        self.assertRaises(timers.TimerStateError, timer.start)
        self.assertRaises(timers.TimerStateError, timer.reset)
        self.assertRaises(timers.TimerStateError, timer.resume)

        timer.stop(stopped=5)
        expect('stop',{'resume':4, 'stopped':5},9,2)

        timer.resume(resume=6)
        expect('resume',{'resume':6, 'stopped':5},9,2)

        self.app.run(2.25)  # Use .25 for float test, since it's binary exact

        timer.stop(stopped=7)
        expect('stop',{'resume':6, 'stopped':7},11.25,4.25)















    def testDirectListener(self):
        # Verify that state machine is correct with a direct listener
        timer = self.getTimer('test.state-machine')
        timer.addListener(self.listener,None)
        self.verifyTimerStateMachine(timer)


    def testPlainIndirectPreListener(self):
        # Verify that state machine is correct with an indirect,
        # non-wildcard listener, added before the timer is created
        testName = 'test.indirect.plain.pre'
        self.addListener(testName,self.listener,None)
        self.verifyTimerStateMachine( self.getTimer(testName) )


    def testPlainIndirectPostListener(self):
        # Verify that state machine is correct with an indirect,
        # non-wildcard listener, added after the timer is created
        testName = 'test.indirect.plain.post'
        timer = self.getTimer(testName)
        self.addListener(testName,self.listener,None)
        self.verifyTimerStateMachine(timer)


    def testWildcardIndirectPreListener(self):
        # Verify that state machine is correct with an indirect
        # wildcard listener, added before the timers are created
        pre = 'test.indirect.wildcard.pre.'
        self.addListener(pre+'*',self.listener,None)
        for suffix in 'one','two','three':
            self.verifyTimerStateMachine( self.getTimer(pre+suffix) )

    def testWildcardIndirectPostListener(self):
        # Verify that state machine is correct with an indirect
        # wildcard listener, added after the timers are created
        pre = 'test.indirect.wildcard.post.'
        timers = [self.getTimer(pre+suffix) for suffix in 'one','two','three']
        self.addListener(pre+'*',self.listener,None)
        map(self.verifyTimerStateMachine, timers )


    def testValidEventNames(self):

        # Verify that ITimer.eventNames are accepted by all
        # listener-registration methods, and that invalid
        # event names are rejected

        l = lambda *args: None

        testName = 'test.event-names'

        timer = self.getTimer(testName)

        for goodName in timers.ITimer.eventNames:
            timer.addListener(l, [goodName])
            self.addListener(testName, l, [goodName])
            self.addListener('test.*', l, [goodName])

        for badName in 'foo bar baz'.split():
            self.assertRaises(
                exceptions.InvalidName,
                timer.addListener, l, [badName]
            )
            self.assertRaises(
                exceptions.InvalidName,
                self.addListener, testName, l, [badName]
            )
            self.assertRaises(
                exceptions.InvalidName,
                self.addListener, 'test.*', l, [badName]
            )


    def testLookupByName(self):
        # verify that 'timer:' URLs map to the same timer service
        for name in 'nametest.1', 'nametest.two', 'nametest.iii':
            timer = self.app.lookupComponent('timer:'+name)
            self.failUnless(timer is self.getTimer(name))




TestClasses = (
    ServiceTests,
)

def test_suite():
    s = []
    for t in TestClasses:
        s.append(makeSuite(t,'test'))

    return TestSuite(s)































