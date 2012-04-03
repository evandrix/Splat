from peak.core import protocols, adapt, NOT_GIVEN
from interfaces import *
from peak.util.EigenData import AlreadyRead
from weakref import ref
from types import MethodType
__all__ = [
    'AnyOf', 'Distributor', 'Value', 'Condition', 'Semaphore',
    'DerivedValue', 'DerivedCondition', 'Observable', 'Readable', 'Writable',
    'AbstractConditional', 'Broadcaster', 'subscribe', 'Null',
]































class NullClass(object):

    """Null condition: never fires, never has a value other than None"""

    __slots__ = ()

    protocols.advise( instancesProvide = [IConditional,IValue] )

    value = property(lambda self: self)

    def __call__(self): pass

    def __repr__(self): return 'events.Null'

    def conjuncts(self): return ()

    def disjuncts(self): return ()

    def __invert__(self):
        return self

    def __and__(self,other):
        return other

    def __or__(self,other):
        return other

    def addCallback(self,cb):
        pass    # we'll never fire, and so can't call back

    def nextAction(self, task=None, state=None):
        pass    # always suspend

Null = NullClass()
def noNew(*args): raise TypeError("Only one Null instance allowed")

NullClass.__new__ = noNew
del NullClass



def subscribe(source,callback):

    """Subscribe 'callback' to an 'IEventSource', using a weak reference

    Usage::
        canceller = events.subscribe(source,callback)

    This function returns a callable that can be used to cancel the
    subscription: just invoke 'canceller()' and no subsequent callbacks will be
    received.  The 'callback' will be wrapped in a weak reference, so if the
    callback goes away, the subscription automatically halts.  (Note that if
    'callback' is a method, then the subscription ends when the object that
    owns the method goes away."""

    canceller = lambda r=None: go and go.pop()

    if isinstance(callback,MethodType):
        cbr = ref(callback.im_self, canceller)
        f = callback.im_func

        def cb(src,evt):
            if go:
                source.addCallback(go[0])
            if go:
                return f(cbr(),src,evt)
    else:
        cbr = ref(callback, canceller)
        def cb(src,evt):
            if go:
                source.addCallback(go[0])
            if go:
                return cbr()(src,evt)

    go = [cb]
    source.addCallback(cb)
    return canceller





class AnyOf(object):

    """Union of multiple event sources

    Example usage::

        timedOut = scheduler.timeout(30)
        untilSomethingHappens = events.AnyOf(stream.dataRcvd, timedOut)

        while not timedOut():
            yield untilSomethingHappens; src,evt = events.resume()
            if src is stream.dataRcvd:
                data = event
                print data

    'AnyOf' fires callbacks whenever any of its actual event sources fire (and
    allows tasks to continue if any of its actual event sources allow it).
    The 'event' it supplies to its user is actually a '(source,event)' tuple
    as shown above, so you can distinguish which of the actual event sources
    fired, as well as receive the event from it.

    Note that callbacks registered with an 'AnyOf' instance will fire at most
    once, even if more than one of the original event sources fires.  Thus,
    you should not assume in a callback or task that the event you received
    is the only one that has occurred.  This is especially true in scheduled
    tasks, where many things may happen between the triggering of an event
    and the resumption of a task that was waiting for the event.
    """

    __slots__ = '_sources'

    protocols.advise(
        instancesProvide=[IEventSource]
    )







    def __new__(klass, *sources):
        if len(sources)==1:
            return adapt(sources[0],IEventSource)
        elif sources:
            self =object.__new__(klass)
            self._sources = adapt(sources, protocols.sequenceOf(IEventSource))
            return self

        raise ValueError, "AnyOf must be called with one or more IEventSources"


    def nextAction(self, task=None, state=None):
        """See 'events.ITaskSwitch.nextAction()'"""

        for source in self._sources:
            action = source.nextAction()

            if action:
                flag = source.nextAction(task,state)

                if state is not None:
                    state.YIELD( (source,state.lastEvent) )
                return flag

        if task is not None:
            self.addCallback(task.step)


    def addCallback(self,func):
        """See 'events.IEventSource.addCallback()'"""

        unfired = [True]
        def onceOnly(source,event):
            if unfired:
                unfired.pop()
                return func(self, (source,event))

        for source in self._sources:
            source.addCallback(onceOnly)


class Observable(object):

    """Base class for a generic event source

    You may subclass this class to create other kinds of event sources: change
    the 'singleFire' class attribute to 'False' in your subclass if you would
    like for events to be broadcast to all callbacks, whether they accept or
    reject the event.
    """

    __slots__ = '_callbacks', '__weakref__', '_disabled', '_savedEvents'

    singleFire = True
    overrunOK  = True

    protocols.advise( instancesProvide=[IEventSource] )

    def __init__(self):
        self._callbacks = []
        self._disabled = 0


    def nextAction(self, task=None, state=None):
        """See 'events.ITaskSwitch.nextAction()'"""
        if task is not None:
            self.addCallback(task.step)


    def addCallback(self,func):
        """See 'events.IEventSource.addCallback()'"""
        self._callbacks.append(func)


    def disable(self):
        """Pause event callbacks"""
        if not self._disabled:
            self._savedEvents = []
        self._disabled += 1



    def enable(self):
        """Resume and send saved events"""

        if not self._disabled:
            raise ValueError("More enable() calls than disable() calls", self)

        self._disabled -= 1

        if not self._disabled:

            while self._savedEvents:
                self._fire(self._savedEvents.pop(0))

            del self._savedEvents


    def _fire(self, event):

        if self._disabled:
            self._buffer(event)
            return

        callbacks, self._callbacks = self._callbacks, []
        count = len(callbacks)

        try:
            if self.singleFire:
                while count:
                    if callbacks.pop(0)(self,event):
                        return
                    count -= 1
            else:
                while count:
                    callbacks.pop(0)(self,event)
                    count -= 1
        finally:
            self._callbacks[0:0] = callbacks      # put back unfired callbacks




    def _buffer(self,event):

        saved = self._savedEvents

        if self.overrunOK:
            if saved:
                del saved[0]

        elif len(saved)>=len(self._callbacks):
            raise ValueError("Can't buffer event", self, event)

        saved.append(event)





























class Distributor(Observable):

    """Sends each event to one callback

    This is perhaps the simplest possible 'IEventSource'.  When its 'send()'
    method is called, the supplied event is passed to any registered
    callbacks.  As soon as a callback "accepts" the event (by returning a true
    value), distribution of the event stops.

    Yielding to an 'events.Distributor' in a task always suspends the task
    until the next 'send()' call on the distributor.
    """

    __slots__ = ()

    overrunOK  = False

    def send(self,event):
        """Send 'event' to one or more callbacks, until accepted"""
        self._fire(event)


class Broadcaster(Observable):

    """Like a distributor, but broadcasting events to all callbacks"""

    __slots__ = ()

    singleFire   = False

    overrunOK  = False

    def send(self,event):
        """Send 'event' to all callbacks"""
        self._fire(event)






class Readable(Observable):

    """Base class for an 'IReadableSource' -- adds a '_value' and '__call__'"""

    __slots__ = '_value'

    singleFire   = False

    protocols.advise(
        instancesProvide=[IReadableSource]
    )

    def __call__(self):
        """See 'events.IReadableSource.__call__()'"""
        return self._value

    def derive(self,func):
        return DerivedValue(lambda: func(self()), self)


class Writable(Readable):

    """Base class for an 'IWritableSource' -- adds a 'set()' method"""

    __slots__ = ()

    protocols.advise(
        instancesProvide=[IWritableSource]
    )

    def set(self,value,force=False):
        """See 'events.IWritableSource.set()'"""
        if force or value<>self._value:
            self._value = value
            self._fire(value)






class AbstractConditional(Observable):

    """Base class for an 'IConditional': fires if and only if value is true"""

    __slots__ = 'cmpval'

    def addCallback(self, func):
        """Add callback, but fire it immediately if value is currently true"""
        value = self()
        if value:
            func(self,value)
        else:
            super(AbstractConditional,self).addCallback(func)

    def nextAction(self, task=None, state=None):
        """Suspend only if current value is false"""
        value = self()
        if value:
            if state is not None:
                state.YIELD(value)
            return True

        if task is not None:
            self.addCallback(task.step)

    def __invert__(self):
        return Not(self)

    def __or__(self,other):
        if self is other or other is Null:
            return self
        return Union(self,other)

    def __and__(self,other):
        if self is other or other is Null:
            return self
        return Intersect(self,other)




    def __cmp__(self,other):
        return cmp(self.cmpval,other)

    def __hash__(self):
        return hash(self.cmpval)

    def disjuncts(self):
        return [self]

    def conjuncts(self):
        return [self]






























class ReadableAsCondition(AbstractConditional):

    """Wrap an 'IReadableSource' as an 'IConditional'"""

    __slots__ = 'value'

    protocols.advise(
        instancesProvide=[IConditional],
        asAdapterForProtocols=[IValue]
    )

    singleFire   = False

    def __init__(self,subject,protocol=None):
        self.value = subject
        super(ReadableAsCondition,self).__init__()
        subscribe(subject, self._set)
        self.cmpval = self.__class__, subject

    def __call__(self): return self.value()

    def derive(self,func):  return self.value.derive(func)

    def _set(self,src,evt):
        if evt:
            self._fire(evt)


class WritableAsCondition(ReadableAsCondition):

    """Wrap an 'IWritableValue' as an 'IConditional'"""

    protocols.advise(
        instancesProvide=[IWritableSource,IConditional],
        asAdapterForProtocols=[IWritableValue]
    )

    def set(self,value,force=False):
        self.value.set(value,force)


class Value(Writable):

    """Broadcast changes in a variable to all observers

    'events.Value()' instances implement a near-trivial version of the
    'Observer' pattern: callbacks can be informed that a change has been
    made to the 'Value'.  Example::

        aValue = events.Value(42)
        assert aValue()==42
        aValue.set(78)  # fires any registered callbacks
        aValue.set(78)  # doesn't fire, value hasn't changed
        aValue.set(78,force=True)   # force firing even though value's the same

    Events are broadcast to all callbacks, whether they "accept" or "reject"
    the event, and tasks yielding to a 'Value' are suspended until the next
    event is broadcast.  The current value of the 'Value' is supplied to
    callbacks and tasks via the 'event' parameter, and the 'Value' itself
    is supplied as the 'source'.  (See 'events.IEventSink'.)
    """

    __slots__ = ()

    protocols.advise(
        instancesProvide=[IValue]
    )

    defaultValue = NOT_GIVEN

    def __init__(self,value=NOT_GIVEN):
        if value is NOT_GIVEN:
            value = self.defaultValue
        self._value = value
        super(Value,self).__init__()

    isTrue = property(lambda self: adapt(self,IConditional))

    isFalse = property(lambda self: ~adapt(self,IConditional))



class DerivedValue(Readable):

    """'DerivedValue(formula, *values)' - a value derived from other values

    Usage::

        # 'derived' changes whenever x or y change
        derived = DerivedValue(lambda: x()+y(), x, y)

    A 'DerivedValue' fires an event equal to 'formula()' whenever any of the
    supplied 'values' fire, and the value of 'formula()' is not equal to its
    last known value (if any).
    """

    __slots__ = '_formula'

    protocols.advise( instancesProvide=[IValue] )

    def __init__(self,formula,*values):
        self._formula = formula
        super(DerivedValue,self).__init__()
        subscribe(AnyOf(*[adapt(v,IValue) for v in values]),self._set) #

    def __call__(self):
        """Get current value of 'formula()'"""
        return self._formula()

    def _set(self,source,event):
        value = self._formula()
        if not hasattr(self,'_value') or self._value<>value:
            self._value = value
            self._fire(value)

    # XXX is there any way to cache?







class Condition(WritableAsCondition):

    """Send callbacks/allow tasks to proceed when condition is true

    A 'Condition' is very similar to a 'Value', except in its yielding and
    callback behavior.  Yielding to a 'Condition' in a task will suspend the
    task *only* if the current value of the 'Condition' is false.  If the
    'Condition' has a true value, the task is allowed to proceed, and
    'events.resume()' will return the value of the 'Condition'.  If the
    'Condition' has a false value, the task will be suspended until
    the value is changed to a true one.

    The behavior for callbacks is similar: when a callback is added with
    'addCallback()', it will be fired immediately if the 'Condition' is true
    at the time the callback is added.  Otherwise, the callback will be fired
    once the 'Condition' becomes true.
    """

    __slots__ = ()

    defaultValue = False

    def __init__(self,value=NOT_GIVEN):
        if value is NOT_GIVEN:
            value = self.defaultValue
        super(Condition,self).__init__(Value(value),IConditional)















class DerivedCondition(ReadableAsCondition):

    """'DerivedCondition(formula, *values)' - derive condition from value(s)

    Usage::

        # 'derived' is re-evaluated whenever x or y change
        derived = DerivedCondition(lambda: x()>=y(), x, y)

    A 'DerivedCondition' fires an event equal to 'formula()' whenever any of
    the supplied 'values' fire, the value of 'formula()' is not equal to its
    last known value (if any), and the value of 'formula()' is true.

    Note that like other 'events.IConditional' implementations, callbacks
    added to a 'DerivedCondition' will be fired immediately if the current
    value of 'formula()' is true, and tasks yielding to a true
    'DerivedCondition' will also proceed immediately without waiting for a
    callback.
    """

    __slots__ = ()

    def __init__(self,formula,*values):
        super(DerivedCondition,self).__init__(
            DerivedValue(formula,*values),IConditional
        )















class Not(DerivedCondition):

    __slots__ = 'baseCondition'

    def __init__(self,baseCondition):
        baseCondition = adapt(baseCondition,IConditional)
        self.baseCondition = baseCondition
        super(Not,self).__init__(
            lambda: not baseCondition.value(), baseCondition,
        )
        self.cmpval = self.__class__,baseCondition

    def __invert__(self):
        return self.baseCondition


class _compound(DerivedCondition):

    __slots__ = 'operands'

    def __init__(self,*args):

        operands = {}

        for op in args:
            for item in self._getPromotable(op):
                operands[item]=1

        operands = list(operands)
        operands.sort()
        self.operands = tuple(operands)

        if len(operands)<2:
            raise TypeError,"Compounds require more than one operand"

        super(_compound,self).__init__(self.formula, *self.operands)
        self.cmpval = self.__class__, self.operands




class Union(_compound):

    __slots__ = ()

    def disjuncts(self):
        return self.operands

    def _getPromotable(self,op):
        return adapt(op,IConditional).disjuncts()

    def formula(self):
        return [b for b in self.operands if b.value()]

    def __invert__(self):
        return Intersect(*[~op for op in self.operands])


class Intersect(_compound):

    __slots__ = ()

    def conjuncts(self):
        return self.operands

    def _getPromotable(self,op):
        return adapt(op,IConditional).conjuncts()

    def formula(self):
        return not [b for b in self.operands if not b.value()]

    def __invert__(self):
        return Union(*[~op for op in self.operands])









class Semaphore(Condition):

    """Allow up to 'n' tasks to proceed simultaneously

    A 'Semaphore' is like a 'Condition', except that it does not broadcast
    its events.  Each event is supplied to callbacks only until one "accepts"
    the event (by returning a true value).

    'Semaphore' instances also have 'put()' and 'take()' methods that
    respectively increase or decrease their value by 1.

    Note that 'Semaphore' does not automatically decrease its count due to
    a callback or task resumption.  You must explicitly 'take()' the
    semaphore in your task or callback to reduce its count.
    """

    __slots__ = ()

    protocols.advise( instancesProvide=[ISemaphore] )

    singleFire   = True
    defaultValue = 0

    def put(self):
        """See 'events.ICondition.put()'"""
        self.set(self()+1)

    def take(self):
        """See 'events.ICondition.take()'"""
        self.set(self()-1)











