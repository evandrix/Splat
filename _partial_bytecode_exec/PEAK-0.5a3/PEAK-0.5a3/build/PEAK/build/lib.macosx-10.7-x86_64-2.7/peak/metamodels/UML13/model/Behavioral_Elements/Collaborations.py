# ------------------------------------------------------------------------------
# Package: peak.metamodels.UML13.model.Behavioral_Elements.Collaborations
# File:    peak\metamodels\UML13\model\Behavioral_Elements\Collaborations.py
# ------------------------------------------------------------------------------

from peak.util.imports import lazyModule as _lazy

_model               = _lazy('peak.model.api')
#_config             = _lazy('peak.config.api')

Core                 = _lazy(__name__, '../../Foundation/Core')

# ------------------------------------------------------------------------------


class Collaboration(Core.GeneralizableElement, Core.Namespace):

    class interaction(_model.StructuralFeature):
        referencedType = 'Interaction'
        referencedEnd = 'context'
        isComposite = True
        sortPosn = 0

    class representedClassifier(_model.StructuralFeature):
        referencedType = 'Foundation/Core/Classifier'
        upperBound = 1
        sortPosn = 1

    class representedOperation(_model.StructuralFeature):
        referencedType = 'Foundation/Core/Operation'
        upperBound = 1
        sortPosn = 2

    class constrainingElement(_model.StructuralFeature):
        referencedType = 'Foundation/Core/ModelElement'
        sortPosn = 3


class ClassifierRole(Core.Classifier):

    class multiplicity(_model.StructuralFeature):
        referencedType = 'Foundation/Data_Types/Multiplicity'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0

    class base(_model.StructuralFeature):
        referencedType = 'Foundation/Core/Classifier'
        lowerBound = 1
        sortPosn = 1

    class availableFeature(_model.StructuralFeature):
        referencedType = 'Foundation/Core/Feature'
        sortPosn = 2

    class message1(_model.StructuralFeature):
        referencedType = 'Message'
        referencedEnd = 'receiver'
        sortPosn = 3

    class message2(_model.StructuralFeature):
        referencedType = 'Message'
        referencedEnd = 'sender'
        sortPosn = 4

    class availableContents(_model.StructuralFeature):
        referencedType = 'Foundation/Core/ModelElement'
        sortPosn = 5


class AssociationRole(Core.Association):

    class multiplicity(_model.StructuralFeature):
        referencedType = 'Foundation/Data_Types/Multiplicity'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0

    class base(_model.StructuralFeature):
        referencedType = 'Foundation/Core/Association'
        upperBound = 1
        sortPosn = 1

    class message(_model.StructuralFeature):
        referencedType = 'Message'
        referencedEnd = 'communicationConnection'
        sortPosn = 2


class AssociationEndRole(Core.AssociationEnd):

    class collaborationMultiplicity(_model.StructuralFeature):
        referencedType = 'Foundation/Data_Types/Multiplicity'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0

    class base(_model.StructuralFeature):
        referencedType = 'Foundation/Core/AssociationEnd'
        upperBound = 1
        sortPosn = 1

    class availableQualifier(_model.StructuralFeature):
        referencedType = 'Foundation/Core/Attribute'
        sortPosn = 2


class Message(Core.ModelElement):

    class interaction(_model.StructuralFeature):
        referencedType = 'Interaction'
        referencedEnd = 'message'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0

    class activator(_model.StructuralFeature):
        referencedType = 'Message'
        referencedEnd = 'message4'
        upperBound = 1
        sortPosn = 1

    class sender(_model.StructuralFeature):
        referencedType = 'ClassifierRole'
        referencedEnd = 'message2'
        upperBound = 1
        lowerBound = 1
        sortPosn = 2

    class receiver(_model.StructuralFeature):
        referencedType = 'ClassifierRole'
        referencedEnd = 'message1'
        upperBound = 1
        lowerBound = 1
        sortPosn = 3

    class predecessor(_model.StructuralFeature):
        referencedType = 'Message'
        referencedEnd = 'message3'
        sortPosn = 4

    class communicationConnection(_model.StructuralFeature):
        referencedType = 'AssociationRole'
        referencedEnd = 'message'
        upperBound = 1
        sortPosn = 5

    class action(_model.StructuralFeature):
        referencedType = 'Common_Behavior/Action'
        upperBound = 1
        lowerBound = 1
        sortPosn = 6

    class message3(_model.StructuralFeature):
        referencedType = 'Message'
        referencedEnd = 'predecessor'
        sortPosn = 7

    class message4(_model.StructuralFeature):
        referencedType = 'Message'
        referencedEnd = 'activator'
        sortPosn = 8


class Interaction(Core.ModelElement):

    class message(_model.StructuralFeature):
        referencedType = 'Message'
        referencedEnd = 'interaction'
        isComposite = True
        lowerBound = 1
        sortPosn = 0

    class context(_model.StructuralFeature):
        referencedType = 'Collaboration'
        referencedEnd = 'interaction'
        upperBound = 1
        lowerBound = 1
        sortPosn = 1

# ------------------------------------------------------------------------------

#_config.setupModule()


