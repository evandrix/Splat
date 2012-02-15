#!/usr/bin/env python
# -*- coding: utf-8 -*-

class class1:
    def func1():
        """ basic print function of class - no self arg """
        print "class1.func1()"
    
    def func2(self):
        """ basic print function of class - with self arg """
        print "class1.func2()"

    def func3(self):
        """ basic function of class - return constant value """
        return 4
    
class class2(class1):
    """ test class inheritance - class2 -> class1 """
    pass

class class3(object):
    """ class object """
    def func1(self, a):
        """ single argument function """
        print a
        return a
    
    def func2(self, a, b=5):
        """ two argument function, with second default(=5) argument """
        return a + b + 60

class class4():
    """ non-inheritance class """
    def __init__(self, a, b):
        """ multiple params class constructor """
        self.a = a
        self.b = b
    
    def __init__(self, a, b, c):
        """ (overloaded) multiple params class constructor """
        self.a = a
        self.b = b
        self.c = c

class BankAccount(object):
    """ Real trivial toy example """
    CLASS_ATTRIBUTE = 'some value'

    def __init__(self, initial_balance=0):
        self.balance = initial_balance
    def deposit(self, amount):
        self.balance += amount
    def withdraw(self, amount):
        self.balance -= amount
    def overdrawn(self):
        return self.balance < 0

    def __str__(self):
# buggy version
        return '%s(%d)' % (__name__, self.balance)
#        return '%s(%d)' % (__name__, self.balance)

def foo(class1, class2, n):
    """ lazy instantiation test for global function """
    class2.func2()
    class1.func3()               # incorrect function
    bank_account = BankAccount(n) # purposely leave out param
#    class1.func1()               # incorrect function
#    bank_account = BankAccount() # purposely leave out param
    print bank_account

# foo(class1(), class2(), 5)
if __name__ == "__main__":
    my_account = BankAccount(15)
    my_account.withdraw(5)
    print my_account.balance
