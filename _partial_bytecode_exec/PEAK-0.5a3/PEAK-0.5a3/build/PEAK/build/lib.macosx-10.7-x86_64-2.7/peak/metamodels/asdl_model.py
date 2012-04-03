# Automatically generated from peak/metamodels/ASDL.asdl

from peak.api import model

class field(model.Struct):

    mdl_isAbstract = True

    class typeName(model.structField):
        referencedType = model.Name
        lowerBound = 1
        sortPosn = 1

    class name(model.structField):
        referencedType = model.Name
        sortPosn = 2

    mdl_subclassNames = (
        'Option',
        'Seq',
        'Plus',
        'Id',
    )


class Option(field):
    pass

class Seq(field):
    pass

class Plus(field):
    pass

class Id(field):
    pass

class constructor_def(model.Struct):

    mdl_isAbstract = True

    mdl_subclassNames = (
        'Constructor',
    )


class Constructor(constructor_def):

    class name(model.structField):
        referencedType = model.Name
        lowerBound = 1
        sortPosn = 1

    class attributes(model.structField):
        referencedType = 'field'
        upperBound = None
        sortPosn = 2



class typedef(model.Struct):

    mdl_isAbstract = True

    class name(model.structField):
        referencedType = model.Name
        lowerBound = 1
        sortPosn = 1

    mdl_subclassNames = (
        'Sum',
        'Product',
    )


class Sum(typedef):

    class types(model.structField):
        referencedType = 'constructor_def'
        lowerBound = 1
        upperBound = None
        sortPosn = 2

    class attributes(model.structField):
        referencedType = 'field'
        upperBound = None
        sortPosn = 3



class Product(typedef):

    class attributes(model.structField):
        referencedType = 'field'
        lowerBound = 1
        upperBound = None
        sortPosn = 2



class module(model.Struct):

    class name(model.structField):
        referencedType = model.Name
        lowerBound = 1
        sortPosn = 1

    class definitions(model.structField):
        referencedType = 'typedef'
        lowerBound = 1
        upperBound = None
        sortPosn = 2



