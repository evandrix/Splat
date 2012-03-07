#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Simple Python object reflector #

class Reflector(object):
    def __init__(self):
        pass

    def print_methods(self):
        """ print all the methods of this object and their docstring """
        print '\n* Methods *'
        for names in dir(self):
            attr = getattr(self,names)
            if callable(attr):
                print names,':', attr.__doc__

    def print_attributes(self):
        """ print all the attributes of this object and their value """
        print '* Attributes *'
        for names in dir(self):
            attr = getattr(self,names)
            if not callable(attr):
                print names,':', attr

if __name__ == "__main__":
    reflector = Reflector()
    reflector.print_attributes()
    reflector.print_methods()

