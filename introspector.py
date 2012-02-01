#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import inspect
import pprint

class Object:
   def __init__(self):
      pass
   def examine(self):
      print self

class Introspector():
    def __init__(self):
        pass
    def _tuple_doc(self):
        return ().__doc__       
    def _dir(self):
        """
            examine several objects using dir()
        """

        o = Object()
        # dir() - returns a sorted list of attributes and methods belonging to an object
        print dir(o)
        print dir(())   # tuple
        print dir([])   # list
        print dir({})   # dict
        print dir(1)
        print dir()     # no arg => names in current scope
        import math, os
        pprint.pprint(dir())
        print dir(len)
        print dir(sys)
        print dir("String")
    def _type(self):
        """
            returns type of an object
        """

        def function(): pass
        class MyObject():
           def __init__(self):
              pass

        o = MyObject()

        print type(1)
        print type("")
        print type([])
        print type({})
        print type(())
        print type(object)
        print type(function)
        print type(MyObject)
        print type(o)
        print type(sys)
    def _id(self):
        """
            returns a special id of an object.
        """

        def fun(): pass
        class MyObject():
           def __init__(self):
              pass

        o = MyObject()

        print id(1)
        print id("")
        print id({})
        print id([])
        print id(sys)
        print id(fun)
        print id(MyObject)
        print id(o)
        print id(object)
    def _various(self):
        
        def fun(): pass
        
        # checks if an object has an attribute
        print hasattr(object, '__doc__')
        print hasattr(fun, '__doc__')
        print hasattr(fun, '__call__')

        # returns the contents of an attribute, if present
        print getattr(object, '__doc__')
        print getattr(fun, '__doc__')
        
        # isinstance function checks if an objects is an instance of a specific class
        # read isinstance.__doc__
        class MyObject():
           def __init__(self):
              pass

        o = MyObject()

        print isinstance(o, MyObject)
        print isinstance(o, object)
        print isinstance(2, int)
        print isinstance('str', str)
        
        # issubclass() function checks if a specific class is a derived class of another class
        # an object is a subclass of itself  
        class Object():
           def __init__(self):
              pass

        class Wall(Object):
           def __init__(self):
              pass

        print issubclass(Object, Object)
        print issubclass(Object, Wall)
        print issubclass(Wall, Object)
        print issubclass(Wall, Wall)
        
        # name, doc
        # __doc__ attribute gives some documentation about an object
        # __name__ attribute holds the name of the object
        def noaction():
           '''A function, which does nothing'''
           pass
        funcs = [noaction, len, str]

        for i in funcs:
           print i.__name__
           print i.__doc__
           print "-" * 75
        
        # callable - checks if an object is a callable object, ie. function
        def fun():
           pass

        print callable(fun)
        print callable([])
        print callable(1)

if __name__ == "__main__":
    """
        introspection is the ability to determine the type of an object at runtime

        everything is an object, with attributes and methods
        introspection dynamically inspects Python objects
    """
    _i = Introspector()

    _i._tuple_doc()
    _i._dir()
    _i._type()
    _i._id()
    _i._various()
    
    # sys module - provides access to system specific variables and functions used or maintained by the interpreter and to functions that interact strongly with the interpreter
    # allows us to query about the Python environment
    # use dir() for full list of variables and functions
    import sys
    print sys.version
    print sys.platform
    print sys.path
    print sys.maxint    # largest positive integer supported by Python's regular integer type
    print sys.executable # name of the executable binary for the Python interpreter
    print sys.argv      # list of command line arguments
    print sys.byteorder # native byte order ('big'/'little' (LSB))

#    globals()
#    locals()
#    help()
