from unittest import TestCase, makeSuite, TestSuite
from peak.util.signature import *
from peak.util.advice import advice

def aFunction(foo,bar,baz):
    pass


class aClass(object):

    def aMethod(self,spam,widget):
        pass

    def classMethod(klass,thingy):
        pass

    classMethod = classmethod(classMethod)

    def staticMethod(johann,gambolputty):
        pass

    staticMethod = staticmethod(staticMethod)

    def advisedMethod(self,someArg):
        pass

    advisedMethod = advice(advisedMethod)














class SignatureTests(TestCase):

    def testFunctionSignature(self):
        args = getPositionalArgs(aFunction)
        self.assertEqual(tuple(args), ('foo','bar','baz'))

    def testInstanceMethodSignature(self):
        args = getPositionalArgs(aClass().aMethod)
        self.assertEqual(tuple(args), ('spam','widget'))
        args = getPositionalArgs(aClass.aMethod)
        self.assertEqual(tuple(args), ('self','spam','widget'))

    def testClassMethodSignature(self):
        args = getPositionalArgs(aClass().classMethod)
        self.assertEqual(tuple(args), ('thingy',))
        args = getPositionalArgs(aClass.classMethod)
        self.assertEqual(tuple(args), ('thingy',))

    def testStaticMethodSignature(self):
        args = getPositionalArgs(aClass().staticMethod)
        self.assertEqual(tuple(args), ('johann','gambolputty',))
        args = getPositionalArgs(aClass.staticMethod)
        self.assertEqual(tuple(args), ('johann','gambolputty',))

    def testAdvisedMethodSignature(self):
        args = getPositionalArgs(aClass().advisedMethod)
        self.assertEqual(tuple(args), ('someArg',))
        args = getPositionalArgs(aClass.advisedMethod)
        self.assertEqual(tuple(args), ('self','someArg',))












TestClasses = (
    SignatureTests,
)

def test_suite():
    s = []
    for t in TestClasses:
        s.append(makeSuite(t,'test'))

    return TestSuite(s)































