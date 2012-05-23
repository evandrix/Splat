# ------------------------------------------------------------------------------
# Package: peak.metamodels.UML13.model.Behavioral_Elements.Use_Cases
# File:    peak\metamodels\UML13\model\Behavioral_Elements\Use_Cases.py
# ------------------------------------------------------------------------------

from peak.util.imports import lazyModule as _lazy

_model               = _lazy('peak.model.api')
#_config             = _lazy('peak.config.api')

Core                 = _lazy(__name__, '../../Foundation/Core')
Common_Behavior      = _lazy(__name__, '../Common_Behavior')

# ------------------------------------------------------------------------------


class UseCase(Core.Classifier):

    class extend(_model.StructuralFeature):
        referencedType = 'Extend'
        referencedEnd = 'extension'
        sortPosn = 0

    class extend2(_model.StructuralFeature):
        referencedType = 'Extend'
        referencedEnd = 'base'
        sortPosn = 1

    class include(_model.StructuralFeature):
        referencedType = 'Include'
        referencedEnd = 'addition'
        sortPosn = 2

    class include2(_model.StructuralFeature):
        referencedType = 'Include'
        referencedEnd = 'base'
        sortPosn = 3

    class extensionPoint(_model.StructuralFeature):
        referencedType = 'ExtensionPoint'
        referencedEnd = 'useCase'
        sortPosn = 4


class Actor(Core.Classifier):
    pass


class UseCaseInstance(Common_Behavior.Instance):
    pass


class Extend(Core.Relationship):

    class condition(_model.StructuralFeature):
        referencedType = 'Foundation/Data_Types/BooleanExpression'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0

    class base(_model.StructuralFeature):
        referencedType = 'UseCase'
        referencedEnd = 'extend2'
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
        referencedEnd = 'extend'
        lowerBound = 1
        sortPosn = 3


class Include(Core.Relationship):

    class addition(_model.StructuralFeature):
        referencedType = 'UseCase'
        referencedEnd = 'include'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0

    class base(_model.StructuralFeature):
        referencedType = 'UseCase'
        referencedEnd = 'include2'
        upperBound = 1
        lowerBound = 1
        sortPosn = 1


class ExtensionPoint(Core.ModelElement):

    class location(_model.StructuralFeature):
        referencedType = 'Foundation/Data_Types/LocationReference'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0

    class useCase(_model.StructuralFeature):
        referencedType = 'UseCase'
        referencedEnd = 'extensionPoint'
        upperBound = 1
        lowerBound = 1
        sortPosn = 1

    class extend(_model.StructuralFeature):
        referencedType = 'Extend'
        referencedEnd = 'extensionPoint'
        sortPosn = 2

# ------------------------------------------------------------------------------

#_config.setupModule()


