from __future__ import generators
from peak.api import NOT_FOUND

__all__ = [
    'query', 'ANY','ALL','AND','OR','NOT', 'FEATURE','EQ','NE','GE','GT',
    'LE','LT','IS','IS_NOT','IN','NOT_IN','TYPE','IS_SUBCLASS','BETWEEN',
]



class reiter(object):

    __slots__ = 'func'

    def __init__(self,func):
        self.func = func

    def __iter__(self):
        return self.func()






















def geniter(gen,filt):
    for ob in gen:
        if filt(ob):
            yield ob

def traverse(obs, name, recurse=0):

    if name[-1:]=='*':
        name=name[:-1]; recurse = 1

    iters = [obs]

    while iters:

        for item in iters.pop():

            isMany = getattr(getattr(item.__class__,name,None),'isMany',NOT_FOUND)
            values = getattr(item,name,NOT_FOUND)

            if values is NOT_FOUND:
                continue

            elif isMany is NOT_FOUND:
                if isinstance(values,(str,unicode)):
                    values = [values]
                else:
                    try:
                        iter(values)
                    except TypeError:
                        values = [values]

            elif not isMany:
                values = [values]

            if recurse:
                values = list(values)
                iters.append(values)

            for v in values: yield v


class query(object):

    """Query iterator"""

    __slots__ = 'generator', 'filter', 'subgen'


    def __init__(self, generator=(), filter=None):
        self.generator, self.filter = generator, filter
        if filter is None:
            self.subgen = generator
        else:
            self.subgen = self

    def __iter__(self):

        if self.filter:
            return geniter(self.generator, self.filter)

        return iter(self.generator)


    def __getitem__(self,key):

        if isinstance(key,str):
            subgen = self.subgen
            return self.__class__(reiter(lambda: traverse(subgen,key)))

        else:
            return self.__class__(self.subgen,key)











def FEATURE(name,predicate):
    return lambda x: predicate(traverse([x],name))


def ANY(name,predicate):
    def ANY(ob):
        for v in traverse([ob],name):
            if predicate(v): return 1
    return ANY


def ALL(name,predicate):
    def ALL(ob):
        for v in traverse([ob],name):
            if not predicate(v): return 0
    return ALL


def EXISTS(name):
    def EXISTS(ob):
        for v in traverse([ob],name):
            return 1
    return EXISTS


def OR(p1,p2):
    return lambda x: p1(x) or p2(x)


def AND(p1,p2):
    return lambda x: p1(x) and p2(x)


def NOT(p1):
    return lambda x: not p1(x)






def EQ(value):
    return lambda x: x==value

def NE(value):
    return lambda x: x!=value

def LE(value):
    return lambda x: x<=value

def LT(value):
    return lambda x: x<=value

def GE(value):
    return lambda x: x>value

def GT(value):
    return lambda x: x>value

def IS(value):
    return lambda x: x is value

def IS_NOT(value):
    return lambda x: x is not value

def IN(value):
    return lambda x: x in value

def NOT_IN(value):
    return lambda x: x not in value

def TYPE(value):
    return lambda x: isinstance(x,value)

def IS_SUBCLASS(value):
    return lambda x: issubclass(x,value)

def BETWEEN(lo,hi):
    return lambda x: lo <= x <= hi



