# ------------------------------------------------------------------------------
# Package: peak.metamodels.UML14.model.Collaborations
# File:    peak\metamodels\UML14\model\Collaborations.py
# ------------------------------------------------------------------------------

from peak.util.imports import lazyModule as _lazy

_model               = _lazy('peak.model.api')
#_config             = _lazy('peak.config.api')

Core                 = _lazy(__name__, '../Core')
Data_Types           = _lazy(__name__, '../Data_Types')
Common_Behavior      = _lazy(__name__, '../Common_Behavior')
Core                 = _lazy(__name__, '../Core')

# ------------------------------------------------------------------------------


class Collaboration(Core.GeneralizableElement, Core.Namespace):

    class interaction(_model.StructuralFeature):
        referencedType = 'Interaction'
        referencedEnd = 'context'
        isComposite = True
        sortPosn = 0

    class representedClassifier(_model.StructuralFeature):
        referencedType = 'Core/Classifier'
        upperBound = 1
        sortPosn = 1

    class representedOperation(_model.StructuralFeature):
        referencedType = 'Core/Operation'
        upperBound = 1
        sortPosn = 2

    class constrainingElement(_model.StructuralFeature):
        referencedType = 'Core/ModelElement'
        sortPosn = 3

    class usedCollaboration(_model.StructuralFeature):
        referencedType = 'Collaboration'
        sortPosn = 4


class ClassifierRole(Core.Classifier):

    class multiplicity(_model.StructuralFeature):
        referencedType = 'Data_Types/Multiplicity'
        upperBound = 1
        sortPosn = 0

    class base(_model.StructuralFeature):
        referencedType = 'Core/Classifier'
        lowerBound = 1
        sortPosn = 1

    class availableFeature(_model.StructuralFeature):
        referencedType = 'Core/Feature'
        sortPosn = 2

    class availableContents(_model.StructuralFeature):
        referencedType = 'Core/ModelElement'
        sortPosn = 3

    class conformingInstance(_model.StructuralFeature):
        referencedType = 'Common_Behavior/Instance'
        sortPosn = 4


class AssociationRole(Core.Association):

    class multiplicity(_model.StructuralFeature):
        referencedType = 'Data_Types/Multiplicity'
        upperBound = 1
        sortPosn = 0

    class base(_model.StructuralFeature):
        referencedType = 'Core/Association'
        upperBound = 1
        sortPosn = 1

    class message(_model.StructuralFeature):
        referencedType = 'Message'
        referencedEnd = 'communicationConnection'
        sortPosn = 2

    class conformingLink(_model.StructuralFeature):
        referencedType = 'Common_Behavior/Link'
        sortPosn = 3


class AssociationEndRole(Core.AssociationEnd):

    class collaborationMultiplicity(_model.StructuralFeature):
        referencedType = 'Data_Types/Multiplicity'
        upperBound = 1
        sortPosn = 0

    class base(_model.StructuralFeature):
        referencedType = 'Core/AssociationEnd'
        upperBound = 1
        sortPosn = 1

    class availableQualifier(_model.StructuralFeature):
        referencedType = 'Core/Attribute'
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
        upperBound = 1
        sortPosn = 1

    class sender(_model.StructuralFeature):
        referencedType = 'ClassifierRole'
        upperBound = 1
        lowerBound = 1
        sortPosn = 2

    class receiver(_model.StructuralFeature):
        referencedType = 'ClassifierRole'
        upperBound = 1
        lowerBound = 1
        sortPosn = 3

    class predecessor(_model.StructuralFeature):
        referencedType = 'Message'
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

    class conformingStimulus(_model.StructuralFeature):
        referencedType = 'Common_Behavior/Stimulus'
        sortPosn = 7


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


class InteractionInstanceSet(Core.ModelElement):

    class context(_model.StructuralFeature):
        referencedType = 'CollaborationInstanceSet'
        referencedEnd = 'interactionInstanceSet'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0

    class interaction(_model.StructuralFeature):
        referencedType = 'Interaction'
        upperBound = 1
        sortPosn = 1

    class participatingStimulus(_model.StructuralFeature):
        referencedType = 'Common_Behavior/Stimulus'
        lowerBound = 1
        sortPosn = 2


class CollaborationInstanceSet(Core.ModelElement):

    class interactionInstanceSet(_model.StructuralFeature):
        referencedType = 'InteractionInstanceSet'
        referencedEnd = 'context'
        isComposite = True
        sortPosn = 0

    class collaboration(_model.StructuralFeature):
        referencedType = 'Collaboration'
        upperBound = 1
        sortPosn = 1

    class participatingInstance(_model.StructuralFeature):
        referencedType = 'Common_Behavior/Instance'
        lowerBound = 1
        sortPosn = 2

    class participatingLink(_model.StructuralFeature):
        referencedType = 'Common_Behavior/Link'
        sortPosn = 3

    class constrainingElement(_model.StructuralFeature):
        referencedType = 'Core/ModelElement'
        sortPosn = 4

# ------------------------------------------------------------------------------

#_config.setupModule()


