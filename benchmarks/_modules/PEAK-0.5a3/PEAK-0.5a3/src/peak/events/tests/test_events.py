"""Test event sources and tasks"""
from __future__ import generators
from unittest import TestCase, makeSuite, TestSuite
from peak.api import *
from peak.tests import testRoot

class BasicTests(TestCase,object):

    kind = "stream"
    sourceType = events.Distributor
    requiredInterface = events.IEventSource
    singleBuffered = False

    def setUp(self):
        self.source = adapt(self.sourceType(),self.requiredInterface)
        self.log = []

    def sink(self,source,event):
        self.log.append((source,event))
        return True

    def reject(self,source,event):
        self.log.append((source,event))

    def doPut(self,value,force=False):
        self.source.send(value)

    def reenter(self,source,event):
        source.addCallback(self.sink)


    def testSuspend(self):
        # Verify that source always suspends
        self.failIf( self.source.nextAction() )

    def testCallback(self):
        # Verify simple callback
        self.source.addCallback(self.sink)
        self.doPut(1)
        self.assertEqual(self.log,[(self.source,1)])

    def testProvides(self):
        adapt(self.source, self.requiredInterface)


    def testMultiCallback(self):

        for i in range(10):
            self.source.addCallback(self.sink)

        if self.kind=="stream":
            # Verify stream for stream types
            for i in range(10):
                self.doPut(i)
            self.assertEqual(self.log,
                [(self.source,i) for i in range(10)]
            )
        else:
            # Verify broadcast for broadcast types
            self.doPut(42)
            self.assertEqual(self.log,
                [(self.source,42) for i in range(10)]
            )


    def testNoReentrance(self):

        self.source.addCallback(self.reenter)

        self.doPut(1,True)
        self.assertEqual(self.log, [])

        self.doPut(2,True)
        self.assertEqual(self.log, [(self.source, 2)])








    def testRejection(self):

        # This test is a little tricky.  If we are using a stream source,
        # we are verifying that it doesn't throw away an event that was
        # rejected by the callback.  If we're using a broadcast source, we're
        # verifying that it sends everything to everybody whether they accept
        # it or reject it.  :)

        self.source.addCallback(self.reject)
        self.source.addCallback(self.sink)
        self.doPut(1)
        self.assertEqual(self.log,[(self.source,1),(self.source,1)])


    def testPauseResume(self):
        self.source.addCallback(self.sink)
        self.source.disable()
        self.doPut(1)
        self.assertEqual(self.log,[])
        self.source.enable()
        self.assertEqual(self.log,[(self.source,1)])

    def testNestedDisable(self):
        self.source.addCallback(self.sink)
        self.source.disable()
        self.source.disable()
        self.doPut(1)
        self.source.enable()
        self.assertEqual(self.log,[])
        self.source.enable()
        self.assertEqual(self.log,[(self.source,1)])

    def testBrokenNesting(self):
        self.source.addCallback(self.sink)
        self.source.disable()
        self.source.enable()
        self.assertEqual(self.log,[])   # nothing should have happened
        self.assertRaises(ValueError, self.source.enable)



    def testBufferSize(self):
        self.source.addCallback(self.sink)
        self.source.disable()
        self.source.disable()
        self.doPut(1)

        if self.singleBuffered:
            # Single-buffered sources fire the last event (at most) when resumed
            self.doPut(2)
            self.source.enable()
            self.assertEqual(self.log,[])
            self.source.enable()
            self.assertEqual(self.log,[(self.source,2)])

        else:
            # More events than callbacks should raise an error
            self.assertRaises(ValueError,self.doPut,2)

            if self.kind=="stream":
                # stream: add a callback for the second event
                self.source.addCallback(self.sink)
            else:
                # broadcast: add a callback for the first event that registers
                # one for the second event
                self.source.addCallback(lambda s,e: s.addCallback(self.sink))

            # Fire the second event
            self.doPut(2)
            self.source.enable()
            self.assertEqual(self.log,[])
            self.source.enable()
            self.assertEqual(self.log,[(self.source,1), (self.source,2)])

    def testDerivation(self):
        if adapt(self.source,events.IReadableSource,None) is not None:
            derived = self.source.derive(lambda x: x*2)
            derived.addCallback(self.sink)
            self.doPut(20)
            self.assertEqual(self.log,[(derived,40)])


class BroadcastTests(BasicTests):

    sourceType = events.Broadcaster
    kind = "broadcast"


class ValueTests(BasicTests):

    sourceType = events.Value
    kind = "broadcast"
    requiredInterface = events.IWritableSource
    singleBuffered = True

    def doPut(self,value,force=False):
        self.source.set(value, force)


class ConditionTests(ValueTests):

    sourceType = events.Condition
    requiredInterface = events.IConditional
    singleBuffered = True

    def reenter(self,source,event):
        self.doPut(False)
        source.addCallback(self.sink)

    def testSuspend(self):
        # Verify that source suspends when value is true

        for f in False, '', 0:
            self.doPut(f,True)
            self.failUnless( self.source.nextAction() is None, self.source())

        for t in True, 'xx', 27:
            self.doPut(t,True)
            self.failIf( self.source.nextAction() is None)




class DerivedValueTests(BasicTests):

    sourceType = events.DerivedValue
    kind = "broadcast"
    singleBuffered = True
    requiredInterface = events.IReadableSource

    def setUp(self):
        self.base = events.Value(0)
        self.source = self.base.derive(lambda base: base*2)
        self.log = []

    def doPut(self,value,force=False):
        try:
            v = value/2.0
        except TypeError:
            v = value[:len(value)/2]
        self.base.set(v, force)


class DerivedConditionTests(DerivedValueTests):

    sourceType = events.DerivedCondition
    requiredInterface = events.IConditional

    reenter = ConditionTests.reenter.im_func
    testSuspend = ConditionTests.testSuspend.im_func

    def setUp(self):
        # we use a condition instead of a value in order to verify that derived
        # values use IValue to bypass the conditionality of their arguments.
        self.base = events.Condition(False)
        self.source = self.sourceType(
            lambda: self.base()*2, events.Value(), self.base  # ensure multi
        )
        self.log = []





class SemaphoreTests(ConditionTests):

    sourceType = events.Semaphore
    kind = "stream"
    requiredInterface = events.ISemaphore

    def reenter(self,source,event):
        source.take()
        source.addCallback(self.sink)


    def testMultiCallback(self):
        # Verify put/take operations
        def take(source,event):
            source.take()
            self.sink(source,event)
            return True
        src = events.Semaphore(3)
        for i in range(10):
            src.addCallback(take)
        self.assertEqual(self.log, [(src,3),(src,2),(src,1)])


    def testNoReentrance(self):
        # Ensure semaphore is reset before starting
        self.source.set(0)
        ConditionTests.testNoReentrance(self)














class AnyOfTests(TestCase):

    def testAnyOfOne(self):
        # Verify that AnyOf(x) is x
        c = events.Condition()
        self.failUnless(events.AnyOf(c) is c)

    def testAnyOfNone(self):
        # Verify that AnyOf() raises ValueError
        self.assertRaises(ValueError, events.AnyOf)

    def testOnlyOnce(self):
        # Verify that AnyOf calls only once per addCallback

        values = [events.Value(v) for v in range(10)]
        any = events.AnyOf(*tuple(values))
        def sink(source,event):
            log.append((source,event))

        for i in range(10):
            # For each possible value, fire that one first, then all the others
            log = []
            any.addCallback(sink)
            values[i].set(-i,True)   # fire the chosen one
            for j in range(10):
                values[j].set(j*2,True)  # fire all the others
            self.assertEqual(log, [(any,(values[i],-i))])

    def testAnySuspend(self):
        c1, c2, c3 = events.Condition(), events.Condition(), events.Condition()
        any = events.AnyOf(c1,c2,c3)
        for i in range(8):
            c1.set(i & 4); c2.set(i & 2); c3.set(i & 1)
            self.assertEqual(
                (any.nextAction() is None), not c1() and not c2() and not c3()
            )

    def testNonEvent(self):
        # Verify that AnyOf(nonevent) raises NotImplementedError
        self.assertRaises(NotImplementedError, events.AnyOf, 42)

    def testRejection(self):
        # Verify that an AnyOf-callback rejects events rejected by its
        # downstream callbacks, or that arrive after the first relevant event
        # for that callback.

        log = []

        def sink(source,event):
            log.append(("sink",source,event))
            return True

        def reject(source,event):
            log.append(("reject",source,event))

        d1, d2 = events.Distributor(), events.Distributor()
        any = events.AnyOf(d1,d2)

        any.addCallback(reject)
        d1.addCallback(sink)
        d1.send(1)
        self.assertEqual(log, [("reject",any,(d1,1)), ("sink",d1,1)])

        log = []
        d2.send(2)  # nothing should happen, since 'reject' already fired
        self.assertEqual(log, [])

        any.addCallback(sink)
        d2.addCallback(sink)
        d2.send(3)
        self.assertEqual(log, [("sink",any,(d2,3))])

        d2.send(4)
        self.assertEqual(log, [("sink",any,(d2,3)),("sink",d2,4)])








class TestTasks(TestCase):

    def spawn(self, iterator):
        return events.Task(iterator)

    def tick(self):
        pass

    def simpleGen(self, log, guard, sentinel):
        while True:
            yield guard; value = events.resume()
            if value == sentinel:
                break
            log.append(value)
            yield value

    def testSimple(self):
        # Test running a single-generator task, receiving values
        # from an event source, verifying its 'isFinished' condition

        v = events.Value()
        log = []
        testData = [1,2,3,5,8,13]

        task = self.spawn( self.simpleGen(log,v,None) )
        self.failIf( task.isFinished() )

        for i in testData:
            v.set(i); self.tick()
            self.failIf( task.isFinished() )

        v.set(None); self.tick()
        self.failUnless( task.isFinished() )
        self.assertEqual(log, testData)







    def testAnySuspend(self):

        testdata = []; log = []
        v1, v2, v3 = events.Value(), events.Value(), events.Value()

        any = events.AnyOf(v1,v2,v3)
        task = self.spawn( self.simpleGen(log, any, (v3,None)) )

        for i in range(5):
            v3.set(i); self.tick();
            testdata.append((v3,i))

        v1.set(True); self.tick()
        v2.set(True); self.tick()
        v1.set(False); self.tick()
        v1.set(True); self.tick()
        v3.set(None); self.tick()

        testdata += [(v1,True),(v2,True),(v1,False),(v1,True)]

        self.failUnless( task.isFinished() )
        self.assertEqual(log, testdata)



















    def testSemaphores(self):

        sem1 = events.Semaphore(5)
        sem2 = events.Semaphore(0)
        log = []

        def gen(me):
            yield sem1; v = events.resume()
            sem1.take()
            log.append((me,v))

            yield sem2; events.resume()
            sem2.take()
            sem1.put()

        tasks = []

        # In the first phase, the first 5 tasks take from sem1, and its
        # available count decreases

        part1 = [(0,5), (1,4), (2,3), (3,2), (4,1)]
        for n in range(10):
            tasks.append( self.spawn( gen(n) ) )

        self.assertEqual(log, part1)

        # In the second phase, the first 5 tasks release their hold on sem1,
        # and the second 5 tasks get to take it, seeing each count as it
        # becomes available.

        part2 = [(5,1),(6,1),(7,1),(8,1),(9,1)]

        for i in range(10):
            sem2.put(); self.tick()
            self.failUnless(tasks[i].isFinished(), i)

        self.assertEqual(log, part1+part2)
        self.assertEqual(sem1(), 5)
        self.assertEqual(sem2(), 0)


    def testSimpleError(self):

        def gen():
            try:
                yield gen1(); events.resume()
            except ValueError:
                log.append("caught")
            else:
                log.append("nocatch")

            # this shouldn't throw an error; i.e.,
            # resuming after catching an error shouldn't reraise the error.
            yield None; events.resume()

        def gen1():
            # We yield first, to ensure that we aren't raising the error
            # while still being called from the first generator (which would
            # be handled by normal Python error trapping)
            yield events.Condition(1); events.resume()

            # Okay, now we're being run by the task itself, so hit it...
            raise ValueError

        log = []
        self.spawn(gen())
        self.assertEqual(log, ["caught"])















    def testUncaughtError(self):

        def gen():
            yield gen1(); events.resume()

        def gen1():
            yield events.Condition(1); events.resume()
            raise ValueError

        self.assertRaises(ValueError, self.spawn, gen())


    def testInterrupt(self):

        c1 = events.Broadcaster()
        c2 = events.Broadcaster()

        def gen(*args):
            yield events.Interrupt(gen1(), c1, *args); events.resume()

        def gen1():
            yield c2; events.resume()

        events.Task(gen())
        self.assertRaises(events.Interruption, c1.send, True)

        events.Task(gen(ValueError))
        self.assertRaises(ValueError, c1.send, True)













class TaskYielding(TestCase):

    simpleGen = TestTasks.simpleGen.im_func

    def testIsEventSource(self):
        log1 = []; v = events.Value()
        log2 = []; testData = [1,2,3,5,8,13]
        task1 = events.Task(self.simpleGen(log1,v,None))
        self.failUnless(adapt(task1,events.IEventSource,None) is not None)
        task2 = events.Task(self.simpleGen(log2,task1,None))
        map(v.set, testData)
        self.assertEqual(testData, log1)
        self.assertEqual(testData, log2)


    def produce(self,data):
        for v in data:
            yield v

    def testNestedYielding(self):
        data = [1,2,3,5,8,13]; log = []
        task = events.Task(self.simpleGen(log, self.produce(data), NOT_GIVEN))
        self.assertEqual(log,data)


















    def testComposition(self):

        def timesTwo(source):
            yield source; yield events.resume()*2

        def asString(source):
            yield source; yield str(events.resume())

        def strDouble(source):
            yield asString(timesTwo(source)); yield events.resume()

        def doubleStr(source):
            yield timesTwo(asString(source)); yield events.resume()

        data = [1,2,3,5,8,13]; v = events.Value()

        for item in data:
            log = []
            task = events.Task(self.simpleGen(log, strDouble(v), NOT_GIVEN))
            v.set(item); self.assertEqual(log,[str(item*2)])

        for item in data:
            log = []
            task = events.Task(self.simpleGen(log, doubleStr(v), NOT_GIVEN))
            v.set(item); self.assertEqual(log,[str(item)*2])
















class ScheduledTasksTest(TestTasks):

    def setUp(self):
        self.scheduler = events.Scheduler()

    def spawn(self,iterator):
        return self.scheduler.spawn(iterator)

    def tick(self):
        self.scheduler.tick()

    def testUncaughtError(self):

        # This also verifies task-switch on sleep, and aborted/not isFinished
        # state of an aborted scheduled task.

        def gen(c):
            yield c; events.resume()
            yield gen1(); events.resume()

        def gen1():
            yield events.Condition(1); events.resume()
            raise ValueError

        c = events.Condition()
        task = self.spawn(gen(c))
        c.set(True) # enable proceeding
        self.assertRaises(ValueError, self.scheduler.tick)

        self.scheduler.tick()   # give the error handler a chance to clean up

        self.assertEqual(task.isFinished(), False)
        self.assertEqual(task.aborted(), True)








class SchedulerTests(TestCase):

    def setUp(self):
        self.time = events.Value(0)
        self.sched = events.Scheduler(self.time)

    def testAvailableTime(self):
        self.assertEqual(self.sched.time_available(), None)

        minDelay = 9999
        for t in 5,15,71,3,2:
            minDelay = min(t,minDelay)
            u = self.sched.until(t)
            self.assertEqual(self.sched.time_available(), minDelay)

        self.time.set(1)
        self.assertEqual(self.sched.time_available(), minDelay-1)
        self.time.set(2)
        self.assertEqual(self.sched.time_available(), minDelay-2)
        self.time.set(3)
        self.sched.tick()   # Clear out the 2 and 3, should now be @5
        self.assertEqual(self.sched.time_available(), 2)    # and delay==2

    def testUntil(self):
        self.verifyAppts(self.sched.until)

    def testTimeouts(self):
        self.time.set(27)   # any old time
        self.verifyAppts(self.sched.timeout)

    def verifyAppts(self,mkAppt):
        offset = self.time()
        appts = 1,2,3,5,8,13
        conds = [mkAppt(t) for t in appts]
        for i in range(20):
            self.time.set(i+offset)
            self.sched.tick()
            for a,c in zip(appts,conds):
                self.assertEqual(a<=i, c())     # Condition met if time expired


    def testShortTick(self):

        stopper = [True]
        stopped = []

        def shortCall(src,evt):
            stopped.append(stopper.pop())
            return True

        sleep = self.sched.sleep(1)
        sleep.addCallback(shortCall)
        sleep.addCallback(shortCall)

        self.time.set(1)
        self.sched.tick(stopped)
        self.assertEqual(stopper, [])
        self.assertEqual(stopped, [True])


    def testIsEmpty(self):
        self.failUnless(self.sched.isEmpty())
        self.sched.sleep(1).addCallback(lambda s,e: True)
        self.failIf(self.sched.isEmpty())
        self.sched.tick()
        self.failIf(self.sched.isEmpty())
        self.time.set(1)
        self.sched.tick()
        self.failUnless(self.sched.isEmpty())













    def testAlarm(self):

        c = events.Broadcaster()

        def gen():
            yield self.sched.alarm(gen1(), 5); events.resume()

        def gen1():
            yield c; events.resume()

        events.Task(gen())

        self.time.set(1)
        self.sched.tick()   # shouldn't fail, timeout hasn't expired yet
        c.send(True)

        self.time.set(6)
        self.sched.tick()   # shouldn't fail, as task has already exited

        events.Task(gen())
        self.time.set(15)
        self.assertRaises(events.TimeoutError, self.sched.tick)



















    def testSleep(self):

        delays = 2,3,5,7
        sleeps = [self.sched.sleep(t) for t in delays]
        log = []

        def callback(s,e):
            log.append((delays[sleeps.index(s)],e))
            s.addCallback(callback)

        for s in sleeps:
            s.addCallback(callback)

        for i in range(20):
            self.time.set(i)
            self.sched.tick()


        # Notice that this ordering may seem counterintuitive for paired-prime
        # products such as '6': one might expect '(2,6)' to come before
        # '(3,6)', for example.  However, the callback occurring at '(3,6)' was
        # registered at time '3', and the callback occurring at '(2,6)' was
        # registered at time '4'.  So, the callbacks are actually being called
        # in the desired, order-preserving fashion, despite the apparently
        # "wrong" order of the data.

        self.assertEqual(log,
            [   (2,2), (3,3), (2,4), (5,5), (3,6), (2,6), (7,7),
                (2,8), (3,9), (5,10), (2,10), (3,12), (2,12),
                (7,14), (2,14), (5,15), (3,15), (2,16), (3,18),
                (2,18),
            ]
        )








class BaseSubscriber(object):
    __slots__ = 'log'

    def __init__(self,log):
        self.log = log

    def method(self,src,evt):
        self.log.append(evt)

    def __call__(self,src,evt):
        self.log.append(evt)


class WeakableSubscriber(BaseSubscriber):
    __slots__ = '__weakref__'


























class SubscriptionTests(TestCase):

    _testSet1 = 1,3,5,9,27,42
    _testSet2 = -15,46,51

    def setUp(self):
        self.log = []
        self.v = events.Value()

    def step1(self,sink):
        canceller = events.subscribe(self.v,sink)
        sink = None # make sure we're not holding a reference
        map(self.v.set, self._testSet1)
        return canceller

    def sink(self,s,e):
        self.log.append(e)

    def step2(self):
        map(self.v.set, self._testSet2)
        self.assertEqual(self.log, list(self._testSet1))

    def testSubscribe(self):
        def sink(s,e):
            self.log.append(e)

        canceller = self.step1(sink)
        canceller()
        self.step2()

    def testWeakFunc(self):
        def sink(s,e):
            self.log.append(e)

        canceller = self.step1(sink)
        del sink    # should go away
        self.step2()




    def testWeakOb(self):
        ob = WeakableSubscriber(self.log)
        canceller = self.step1(ob)
        del ob    # should go away
        self.step2()

    def testWeakObMethod(self):
        ob = WeakableSubscriber(self.log)
        canceller = events.subscribe(self.v,ob.method)
        map(self.v.set, self._testSet1)
        del ob    # should go away
        self.step2()





























class LogicTests(TestCase):

    """Verify that boolean expressions are equal to their simpler forms

    We want the following transformations to occur wherever possible:

        * NOT(OR(x,y)) -> AND(NOT(x),NOT(y))

        * AND(x,AND(y,z)) -> AND(x,y,z)

        * OR(x,OR(y,z)) -> OR(x,y,z)

        * NOT(NOT(x)) -> x

    The test cases in this class will verify that expressions are as simple
    as possible, but no simpler.  :)
    """

    def setUp(self):
        self.condX = events.Condition()
        self.condY = events.Condition()
        self.condZ = events.Condition()

    def testBooleanCommutativity(self):
        x,y,z = self.condX, self.condY, self.condZ
        self.assertEqual( (x & y & z), (z & y & x) )
        self.assertNotEqual( (x & y & z), (x & y) )
        self.assertEqual( (x|y|z), (z|y|x) )
        self.assertNotEqual( (x|y|z), (x|y) )

    def testBooleanEqualities(self):
        x,y,z = self.condX, self.condY, self.condZ
        if x is not events.Null and y is not events.Null:
            self.assertNotEqual( (x&y), (x|y) )
        self.assertEqual(x,x)
        self.assertNotEqual(x,y)
        self.assertEqual( (x|x), x )
        self.assertEqual( (x&x), x )
        self.assertEqual( (x&y)&(x&y&z), (x&y&z) )


    def testBooleanAssociativity(self):
        x,y,z = self.condX, self.condY, self.condZ
        self.assertEqual( (x&(y&z)), ((x&y)&z) )
        self.assertEqual( (x|(y|z)), ((x|y)|z) )
        if x is not events.Null and y is not events.Null:
            self.assertNotEqual( (x|(y&z)), (x&y)|z )
            self.assertNotEqual( (x&(y|z)), ((x|y)&z) )


    def testNegation(self):
        x,y,z = self.condX, self.condY, self.condZ

        self.assertEqual( x, ~~x)
        self.assertEqual( ~x, ~x)
        self.assertEqual( ~x, ~~~x)
        if x is not events.Null and y is not events.Null:
            self.assertNotEqual( x, ~x)
            self.assertNotEqual( ~(x&y), (x&y) )
            self.assertNotEqual( ~(x&y), (x|y) )
        self.assertEqual( ~(x&y), (~x|~y) )
        self.assertEqual( ~~(x&y), (x&y) )
        self.assertEqual(~((x|y)&z), (~(x|y)|~z) )
        self.assertEqual((~(x&y)&~z), ~((x&y)|z) )


class NullTests1(LogicTests):

    """Test logic w/nulls in 1st position"""

    def setUp(self):
        LogicTests.setUp(self)
        self.condX = events.Null

class NullTests2(LogicTests):

    """Test logic w/nulls in 2nd position"""

    def setUp(self):
        LogicTests.setUp(self)
        self.condY = events.Null

class SemanticsTests(TestCase):

    def testValuesAndConditions(self):
        v1 = events.Value(False)
        v2 = events.Condition(True)
        self.failIf( (v2 & v1.isTrue)() )
        self.failUnless( (v2|v1.isTrue)() )
        self.failIf(v1())
        self.failUnless((~v1.isTrue)())
        self.failUnless(v2())
        self.failIf((~v2)())
        self.failIf( (~(v2|v1))())
        self.failIf(v2.value.isFalse())

    def testRaceCondition(self):
        # ensure that derived values don't race with queriers

        def sink(src,evt):
            self.assertEqual( derived(), base()*2 )

        base = events.Value(1)
        base.addCallback(sink)  # subscribe this first
        derived = events.DerivedValue(lambda:base()*2, base)
        self.assertEqual( derived(), base()*2 )
        base.set(2)
















class AdviceTests(TestCase):

    def testAdvice(self):

        class MyClass(binding.Component):

            def aTask(self):
                yield events.Condition(True); events.resume()

            aTask = binding.Make( events.taskFactory(aTask) )

            def taskedMethod(self):
                yield events.Condition(True); events.resume()

            taskedMethod = events.taskFactory(taskedMethod)

        ob = MyClass()
        self.failIf(adapt(ob.aTask, events.ITask,None) is None)
        self.failIf(adapt(ob.taskedMethod(), events.ITask,None) is None)






















TestClasses = (
    BasicTests, ValueTests, ConditionTests, SemaphoreTests, AnyOfTests,
    TestTasks, ScheduledTasksTest, SchedulerTests, AdviceTests,
    DerivedValueTests, DerivedConditionTests, BroadcastTests, TaskYielding,
    SubscriptionTests, LogicTests, NullTests1, NullTests2, SemanticsTests
)

def test_suite():
    s = []
    for t in TestClasses:
        s.append(makeSuite(t,'test'))

    return TestSuite(s)




























