#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Generator - Metaclass submodule #

# Custom AttributeError (obj, attr)
class MetaAttributeError(AttributeError):
    target_object = missing_attr = None

    def __init__(self, target_object, missing_attr):
        self.target_object = target_object
        self.missing_attr  = missing_attr
        self.parent_exception = AttributeError

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return str(self.target_object) + '_' + str(self.missing_attr)

# Custom metaclass parameter object (closure)
class MetaParam(type):
    registry = {}
    def __repr__(cls):
        return cls.__name__
    def __new__(cls, name, bases, dct):
        """ controls (class) object creation """
        #print "Allocating memory for class", name
        #print meta
        #print bases
        #pprint(dct)
        rv = type.__new__(cls, name, bases, dct)
        cls.registry[name] = rv
        return rv
    def __init__(cls, name, bases, dct):
        """
            called when metaclass is constructed
            controls initialisation of new object (after creation)
        """
        #print "Initializing class", name
        #print cls
        #print bases
        #pprint(dct)
        super(MetaParam, cls).__init__(name, bases, dct)
    def __call__(cls, *vargs, **kwargs):
        """
            called when instance is instantiated
            instance methods added here will apply to instance
            can also return another class' instance (if factory)
        """
        return type.__call__(cls, *vargs, **kwargs)
    def __getitem__(cls, name):
        return cls.registry[name]

def create_metaparam(index, attr=None, dct={}):
    class Param(object):
        __metaclass__ = MetaParam
        def __new__(cls, *args):
            """
                first step in instance creation
                controls creation of new instance
                used for subclassing immutable type, eg. str,int,unicode,tuple
            """
            return super(Param, cls).__new__(cls, args)
        def __init__(self, index, attr=None, dct={}):
            """
                controls initialisation of new instance
            """
            self.index = index + 1  # 1-based index
            self.attr  = attr
            self.dct   = dct
            if self.attr:
                self.__class__.__name__ = "Param%d_%s" % (self.index,self.attr)
            else:
                self.__class__.__name__ = "Param%d" % self.index

            for key, value in dct.iteritems():
                if not key.startswith("__"):
                    setattr(self, key, value)
        def __getattr__(self, name):
            raise MetaAttributeError(self, name)
        def __str__(self):
            return repr(self)
        def __repr__(self):
            return self.__class__.__name__
    return Param(index, attr, dct)
