"""
This is like the unittest module, except that test methods may take
arguments.  You must declare each argument with a default value which
names a test-data generator.  The peckcheck module will then peck at
your test methods with a bunch of generated values.

Sample usage:

    from peckcheck import TestCase, an_int, main

    class TestArithmetic(TestCase):
        def testAddCommutes(self, x=an_int, y=an_int):
            assert x + y == y + x
        def testAddAssociates(self, x=an_int, y=an_int, z=an_int):
            assert x + (y + z) == (x + y) + z

    if __name__ == '__main__':
        main()

You can create a test-data generator of your own by defining a
function with one parameter, the size bound.  For example:

    def a_weekday(size):
        import random
        return random.choice(['Sun','Mon','Tue','Wed','Thu','Fri','Sat'])

Send bug reports to the author, Darius Bacon <darius@wry.me>.

See http://www.math.chalmers.se/~rjmh/QuickCheck/ for the original
automatic specification-based testing tool.

See http://pyunit.sourceforge.net/ for the unittest module this module
is derived from.

Copyright (c) 1999, 2000, 2001 Steve Purcell
Copyright (c) 2004 Darius Bacon
This module is free software, and you may redistribute it and/or modify
it under the same terms as Python itself, so long as this copyright message
and disclaimer are retained in their original form.

IN NO EVENT SHALL THE AUTHOR BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT,
SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OF
THIS CODE, EVEN IF THE AUTHOR HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH
DAMAGE.

THE AUTHOR SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE.  THE CODE PROVIDED HEREUNDER IS ON AN "AS IS" BASIS,
AND THERE IS NO OBLIGATION WHATSOEVER TO PROVIDE MAINTENANCE,
SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS.
"""

import random
import sys
import unittest

# Some random data generators to start with.

def a_boolean(size):
    return random.choice([False, True])

def an_index(size):
    return random.randint(0, size - 1)

def an_int(size):
    return random.randint(-size, size - 1)

def a_float(size):
    return (random.random() - 0.5) * (2*size)

def a_char(size):
    return chr(random.randint(0, 255))

def a_printable_char(size):
    return chr(32 + random.randint(0, 126-32))

def a_string(size):
    return string.join(a_list(a_char)(size), '')

def a_list(generator):
    return lambda size: [generator(size) for _ in range(size)]

def a_tuple(generator):
    return lambda size: tuple(a_list(generator)(size))

def a_choice(*generators):
    return lambda size: random.choice(generators)(size)

def a_tuple_with(*generators):
    return lambda size: tuple([g(size) for g in generators])

size = 20  # Default random test case size (with a type-dependent meaning)


# Help functions for writing generators.

def weighted_choice(choices):
    total = sum([weight for (weight, _) in choices])
    i = random.randint(0, total - 1)
    for weight, choice in choices:
        i -= weight
        if i < 0: 
            return choice()
    raise 'Bug'


# The rest of the code in this module depends on unittest internals.

class TestCase(unittest.TestCase):

    """A kind of test case that can bind parameters with random values."""

    # It sucks to replicate this entire method from unittest.py just
    # to hook in the arguments to the testMethod, but this actually 
    # seems like the simplest way to do it without modifying unittest.py.

    def __call__(self, result=None):
        if result is None: result = self.defaultTestResult()
        result.startTest(self)
        testMethod = getattr(self, self._testMethodName)
        try:
            try:
                self.setUp()
            except KeyboardInterrupt:
                raise
            except:
                result.addError(self, sys.exc_info())
                return

            arguments = _generateArguments(testMethod)  # Added code

            ok = 0
            try:
                testMethod(*arguments)                  # Changed code
                ok = 1
            except self.failureException:
                result.addFailure(self, sys.exc_info())
            except KeyboardInterrupt:
                raise
            except:
                result.addError(self, sys.exc_info())

            try:
                self.tearDown()
            except KeyboardInterrupt:
                raise
            except:
                result.addError(self, sys.exc_info())
                ok = 0
            if ok: result.addSuccess(self)
        finally:
            result.stopTest(self)

def _generateArguments(method):
    generators = method.im_func.func_defaults or ()
    return [g(size) for g in generators]


# Misc extra folderol to get the framework to deal with our new test case
# type approximately as we'd want.

num_trials = 100

class TestLoader(unittest.TestLoader):

    def loadTestsFromTestCase(self, testCaseClass):
        """Return a suite of all tests cases contained in testCaseClass"""
        tests = []
        for name in self.getTestCaseNames(testCaseClass):
            test = testCaseClass(name)
            if _expectsArguments(test, name):
                # Here is what's different from the superclass:
                # test cases that expect random arguments get repeated
                # a bunch of times.
                tests.extend([testCaseClass(name) for _ in range(num_trials)])
            else:
                tests.append(test)
        return self.suiteClass(tests)

def _expectsArguments(test, name):
    return not not getattr(test, name).im_func.func_defaults 

class _TextTestResult(unittest._TextTestResult):
    """A result that prints each failure case only once.  With random
    testing we can get lots of repeats and we don't need all that noise."""

    def printErrorList(self, flavour, errors):
        seen = {}
        for test, err in errors:
            descr = self.getDescription(test)
            if descr not in seen:
                seen[descr] = True
                self.stream.writeln(self.separator1)
                self.stream.writeln('%s: %s' % (flavour, descr))
                self.stream.writeln(self.separator2)
                self.stream.writeln('%s' % err)

class TextTestRunner(unittest.TextTestRunner):

    def _makeResult(self):
        return _TextTestResult(self.stream, self.descriptions, self.verbosity)

defaultTestLoader = TestLoader()

class TestProgram(unittest.TestProgram):

    # Overridden to stick in our own defaultTestLoader.
    def __init__(self, module='__main__', defaultTest=None,
                 argv=None, testRunner=None, testLoader=defaultTestLoader):
        unittest.TestProgram.__init__(self, module, defaultTest, argv, 
                                      testRunner, testLoader)

    # Overridden to stick in our own TextTestRunner.
    def runTests(self):
        if self.testRunner is None:
            self.testRunner = TextTestRunner(verbosity=self.verbosity)
        result = self.testRunner.run(self.test)
        sys.exit(not result.wasSuccessful())

main = TestProgram

# We import these remaining names so peckcheck can serve as a drop-in
# replacement for the unittest module.
from unittest import TestResult, TestSuite, FunctionTestCase
                     
if __name__ == '__main__':
    main(module=None)
