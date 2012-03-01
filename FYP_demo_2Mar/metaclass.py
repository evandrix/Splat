#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Generator - Metaclass submodule #
#

# Custom AttributeError (obj, attr)
class MetaAttributeError(Exception):
    target_object = missing_attr = None

    def __init__(self, target_object, missing_attr):
        self.target_object = target_object
        self.missing_attr  = missing_attr

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return str(self.target_object) + '_' + str(self.missing_attr)

# Custom metaclass parameter object (closure)
class MetaParam(type):
    def __repr__(cls):
        return c.__name__
    def __new__(meta, name, bases, dct):
        """ controls (class) object creation """
        #print "Allocating memory for class", name
        #print meta
        #print bases
        #pprint(dct)
        return super(MyMeta, meta).__new__(meta, name, bases, dct)
    def __init__(cls, name, bases, dct):
        """
            called when metaclass is constructed
            controls initialisation of new object (after creation)
        """
        #print "Initializing class", name
        #print cls
        #print bases
        #pprint(dct)
        super(MyMeta, cls).__init__(name, bases, dct)
    def __call__(cls, *vargs, **kwargs):
        """
            called when instance is instantiated
            instance methods added here will apply to instance
            can also return another class' instance (if factory)
        """
        return type.__call__(cls, *vargs, **kwargs)

def create_metaparam(index):
    class Param(object):
        __metaclass__ = MetaParam
        def __new__(cls, *args):
            """
                first step in instance creation
                controls creation of new instance
                used for subclassing immutable type, eg. str,int,unicode,tuple
            """
            return super(MyParam, cls).__new__(cls, args)
        def __init__(self, index):
            """
                controls initialisation of new instance
            """
            self.index = index + 1  # 1-based index
            self.__class__.__name__ = "Param%d" % self.index
        def __getattr__(self, name):
            raise MetaAttributeError(self, name)
        def __str__(self):
            return repr(self)
        def __repr__(self):
            return self.__class__.__name__
    return Param(index)
