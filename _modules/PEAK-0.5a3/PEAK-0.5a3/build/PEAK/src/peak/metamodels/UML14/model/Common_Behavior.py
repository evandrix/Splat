# ------------------------------------------------------------------------------
# Package: peak.metamodels.UML14.model.Common_Behavior
# File:    peak\metamodels\UML14\model\Common_Behavior.py
# ------------------------------------------------------------------------------

from peak.util.imports import lazyModule as _lazy

_model               = _lazy('peak.model.api')
#_config             = _lazy('peak.config.api')

Core                 = _lazy(__name__, '../Core')
Data_Types           = _lazy(__name__, '../Data_Types')
Core                 = _lazy(__name__, '../Core')

# ------------------------------------------------------------------------------


class Instance(Core.ModelElement):

    mdl_isAbstract = True

    class classifier(_model.StructuralFeature):
        referencedType = 'Core/Classifier'
        lowerBound = 1
        sortPosn = 0

    class linkEnd(_model.StructuralFeature):
        referencedType = 'LinkEnd'
        referencedEnd = 'instance'
        sortPosn = 1

    class slot(_model.StructuralFeature):
        referencedType = 'AttributeLink'
        referencedEnd = 'instance'
        isComposite = True
        sortPosn = 2

    class componentInstance(_model.StructuralFeature):
        referencedType = 'ComponentInstance'
        referencedEnd = 'resident'
        upperBound = 1
        sortPosn = 3

    class ownedInstance(_model.StructuralFeature):
        referencedType = 'Instance'
        isComposite = True
        sortPosn = 4

    class ownedLink(_model.StructuralFeature):
        referencedType = 'Link'
        isComposite = True
        sortPosn = 5


class Signal(Core.Classifier):
    pass


class Action(Core.ModelElement):

    mdl_isAbstract = True

    class recurrence(_model.StructuralFeature):
        referencedType = 'Data_Types/IterationExpression'
        upperBound = 1
        sortPosn = 0

    class target(_model.StructuralFeature):
        referencedType = 'Data_Types/ObjectSetExpression'
        upperBound = 1
        sortPosn = 1

    class isAsynchronous(_model.StructuralFeature):
        referencedType = 'Data_Types/Boolean'
        upperBound = 1
        lowerBound = 1
        sortPosn = 2

    class script(_model.StructuralFeature):
        referencedType = 'Data_Types/ActionExpression'
        upperBound = 1
        sortPosn = 3

    class actualArgument(_model.StructuralFeature):
        referencedType = 'Argument'
        referencedEnd = 'action'
        isComposite = True
        sortPosn = 4

    class actionSequence(_model.StructuralFeature):
        referencedType = 'ActionSequence'
        referencedEnd = 'action'
        upperBound = 1
        sortPosn = 5


class CreateAction(Action):

    class instantiation(_model.StructuralFeature):
        referencedType = 'Core/Classifier'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0


class DestroyAction(Action):
    pass


class UninterpretedAction(Action):
    pass


class AttributeLink(Core.ModelElement):

    class attribute(_model.StructuralFeature):
        referencedType = 'Core/Attribute'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0

    class value(_model.StructuralFeature):
        referencedType = 'Instance'
        upperBound = 1
        lowerBound = 1
        sortPosn = 1

    class instance(_model.StructuralFeature):
        referencedType = 'Instance'
        referencedEnd = 'slot'
        upperBound = 1
        sortPosn = 2

    class linkEnd(_model.StructuralFeature):
        referencedType = 'LinkEnd'
        referencedEnd = 'qualifiedValue'
        upperBound = 1
        sortPosn = 3


class Object(Instance):
    pass


class Link(Core.ModelElement):

    class association(_model.StructuralFeature):
        referencedType = 'Core/Association'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0

    class connection(_model.StructuralFeature):
        referencedType = 'LinkEnd'
        referencedEnd = 'link'
        isComposite = True
        lowerBound = 2
        sortPosn = 1


class LinkObject(Object, Link):
    pass


class DataValue(Instance):
    pass


class CallAction(Action):

    class operation(_model.StructuralFeature):
        referencedType = 'Core/Operation'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0


class SendAction(Action):

    class signal(_model.StructuralFeature):
        referencedType = 'Signal'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0


class ActionSequence(Action):

    class action(_model.StructuralFeature):
        referencedType = 'Action'
        referencedEnd = 'actionSequence'
        isComposite = True
        sortPosn = 0


class Argument(Core.ModelElement):

    class value(_model.StructuralFeature):
        referencedType = 'Data_Types/Expression'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0

    class action(_model.StructuralFeature):
        referencedType = 'Action'
        referencedEnd = 'actualArgument'
        upperBound = 1
        sortPosn = 1


class Reception(Core.BehavioralFeature):

    class specification(_model.StructuralFeature):
        referencedType = 'Data_Types/String'
        upperBound = 1
        sortPosn = 0

    class isRoot(_model.StructuralFeature):
        referencedType = 'Data_Types/Boolean'
        upperBound = 1
        lowerBound = 1
        sortPosn = 1

    class isLeaf(_model.StructuralFeature):
        referencedType = 'Data_Types/Boolean'
        upperBound = 1
        lowerBound = 1
        sortPosn = 2

    class isAbstract(_model.StructuralFeature):
        referencedType = 'Data_Types/Boolean'
        upperBound = 1
        lowerBound = 1
        sortPosn = 3

    class signal(_model.StructuralFeature):
        referencedType = 'Signal'
        upperBound = 1
        lowerBound = 1
        sortPosn = 4


class LinkEnd(Core.ModelElement):

    class instance(_model.StructuralFeature):
        referencedType = 'Instance'
        referencedEnd = 'linkEnd'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0

    class link(_model.StructuralFeature):
        referencedType = 'Link'
        referencedEnd = 'connection'
        upperBound = 1
        lowerBound = 1
        sortPosn = 1

    class associationEnd(_model.StructuralFeature):
        referencedType = 'Core/AssociationEnd'
        upperBound = 1
        lowerBound = 1
        sortPosn = 2

    class qualifiedValue(_model.StructuralFeature):
        referencedType = 'AttributeLink'
        referencedEnd = 'linkEnd'
        isComposite = True
        sortPosn = 3


class ReturnAction(Action):
    pass


class TerminateAction(Action):
    pass


class Stimulus(Core.ModelElement):

    class argument(_model.StructuralFeature):
        referencedType = 'Instance'
        sortPosn = 0

    class sender(_model.StructuralFeature):
        referencedType = 'Instance'
        upperBound = 1
        lowerBound = 1
        sortPosn = 1

    class receiver(_model.StructuralFeature):
        referencedType = 'Instance'
        upperBound = 1
        lowerBound = 1
        sortPosn = 2

    class communicationLink(_model.StructuralFeature):
        referencedType = 'Link'
        upperBound = 1
        sortPosn = 3

    class dispatchAction(_model.StructuralFeature):
        referencedType = 'Action'
        upperBound = 1
        lowerBound = 1
        sortPosn = 4


class Exception(Signal):
    pass


class ComponentInstance(Instance):

    class nodeInstance(_model.StructuralFeature):
        referencedType = 'NodeInstance'
        referencedEnd = 'resident'
        upperBound = 1
        sortPosn = 0

    class resident(_model.StructuralFeature):
        referencedType = 'Instance'
        referencedEnd = 'componentInstance'
        sortPosn = 1


class NodeInstance(Instance):

    class resident(_model.StructuralFeature):
        referencedType = 'ComponentInstance'
        referencedEnd = 'nodeInstance'
        sortPosn = 0


class SubsystemInstance(Instance):
    pass

# ------------------------------------------------------------------------------

#_config.setupModule()


