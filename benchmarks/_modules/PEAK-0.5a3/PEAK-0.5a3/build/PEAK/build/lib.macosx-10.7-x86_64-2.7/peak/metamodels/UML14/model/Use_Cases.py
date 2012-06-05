# ------------------------------------------------------------------------------
# Package: peak.metamodels.UML14.model.Use_Cases
# File:    peak\metamodels\UML14\model\Use_Cases.py
# ------------------------------------------------------------------------------

from peak.util.imports import lazyModule as _lazy

_model               = _lazy('peak.model.api')
#_config             = _lazy('peak.config.api')

Data_Types           = _lazy(__name__, '../Data_Types')
Core                 = _lazy(__name__, '../Core')
Common_Behavior      = _lazy(__name__, '../Common_Behavior')
Core                 = _lazy(__name__, '../Core')
Common_Behavior      = _lazy(__name__, '../Common_Behavior')

# ------------------------------------------------------------------------------


class UseCase(Core.Classifier):

    class extend(_model.StructuralFeature):
        referencedType = 'Extend'
        referencedEnd = 'extension'
        sortPosn = 0

    class include(_model.StructuralFeature):
        referencedType = 'Include'
        referencedEnd = 'base'
        sortPosn = 1

    class extensionPoint(_model.StructuralFeature):
        referencedType = 'ExtensionPoint'
        referencedEnd = 'useCase'
        isComposite = True
        sortPosn = 2


class Actor(Core.Classifier):
    pass


class UseCaseInstance(Common_Behavior.Instance):
    pass


class Extend(Core.Relationship):

    class condition(_model.StructuralFeature):
        referencedType = 'Data_Types/BooleanExpression'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0

    class base(_model.StructuralFeature):
        referencedType = 'UseCase'
        upperBound = 1
        lowerBound = 1
        sortPosn = 1

    class extension(_model.StructuralFeature):
        referencedType = 'UseCase'
        referencedEnd = 'extend'
        upperBound = 1
        lowerBound = 1
        sortPosn = 2

    class extensionPoint(_model.StructuralFeature):
        referencedType = 'ExtensionPoint'
        lowerBound = 1
        sortPosn = 3


class Include(Core.Relationship):

    class addition(_model.StructuralFeature):
        referencedType = 'UseCase'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0

    class base(_model.StructuralFeature):
        referencedType = 'UseCase'
        referencedEnd = 'include'
        upperBound = 1
        lowerBound = 1
        sortPosn = 1


class ExtensionPoint(Core.ModelElement):

    class location(_model.StructuralFeature):
        referencedType = 'Data_Types/LocationReference'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0

    class useCase(_model.StructuralFeature):
        referencedType = 'UseCase'
        referencedEnd = 'extensionPoint'
        upperBound = 1
        lowerBound = 1
        sortPosn = 1

# ------------------------------------------------------------------------------

#_config.setupModule()


