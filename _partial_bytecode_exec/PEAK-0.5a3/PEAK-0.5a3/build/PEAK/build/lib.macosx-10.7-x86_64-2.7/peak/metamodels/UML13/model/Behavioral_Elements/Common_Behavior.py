# ------------------------------------------------------------------------------
# Package: peak.metamodels.UML13.model.Behavioral_Elements.Common_Behavior
# File:    peak\metamodels\UML13\model\Behavioral_Elements\Common_Behavior.py
# ------------------------------------------------------------------------------

from peak.util.imports import lazyModule as _lazy

_model               = _lazy('peak.model.api')
#_config             = _lazy('peak.config.api')

Core                 = _lazy(__name__, '../../Foundation/Core')

# ------------------------------------------------------------------------------


class Instance(Core.ModelElement):

    class classifier(_model.StructuralFeature):
        referencedType = 'Foundation/Core/Classifier'
        lowerBound = 1
        sortPosn = 0

    class attributeLink(_model.StructuralFeature):
        referencedType = 'AttributeLink'
        referencedEnd = 'value'
        sortPosn = 1

    class linkEnd(_model.StructuralFeature):
        referencedType = 'LinkEnd'
        referencedEnd = 'instance'
        sortPosn = 2

    class slot(_model.StructuralFeature):
        referencedType = 'AttributeLink'
        referencedEnd = 'instance'
        isComposite = True
        sortPosn = 3

    class stimulus1(_model.StructuralFeature):
        referencedType = 'Stimulus'
        referencedEnd = 'argument'
        sortPosn = 4

    class stimulus2(_model.StructuralFeature):
        referencedType = 'Stimulus'
        referencedEnd = 'receiver'
        sortPosn = 5

    class stimulus3(_model.StructuralFeature):
        referencedType = 'Stimulus'
        referencedEnd = 'sender'
        sortPosn = 6

    class componentInstance(_model.StructuralFeature):
        referencedType = 'ComponentInstance'
        referencedEnd = 'resident'
        upperBound = 1
        sortPosn = 7


class Signal(Core.Classifier):

    class reception(_model.StructuralFeature):
        referencedType = 'Reception'
        referencedEnd = 'signal'
        sortPosn = 0

    class context(_model.StructuralFeature):
        referencedType = 'Foundation/Core/BehavioralFeature'
        sortPosn = 1

    class sendAction(_model.StructuralFeature):
        referencedType = 'SendAction'
        referencedEnd = 'signal'
        sortPosn = 2


class Action(Core.ModelElement):

    mdl_isAbstract = True

    class recurrence(_model.StructuralFeature):
        referencedType = 'Foundation/Data_Types/IterationExpression'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0

    class target(_model.StructuralFeature):
        referencedType = 'Foundation/Data_Types/ObjectSetExpression'
        upperBound = 1
        lowerBound = 1
        sortPosn = 1

    class isAsynchronous(_model.StructuralFeature):
        referencedType = 'Foundation/Data_Types/Boolean'
        upperBound = 1
        lowerBound = 1
        sortPosn = 2

    class script(_model.StructuralFeature):
        referencedType = 'Foundation/Data_Types/ActionExpression'
        upperBound = 1
        lowerBound = 1
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

    class stimulus(_model.StructuralFeature):
        referencedType = 'Stimulus'
        referencedEnd = 'dispatchAction'
        sortPosn = 6


class CreateAction(Action):

    class instantiation(_model.StructuralFeature):
        referencedType = 'Foundation/Core/Classifier'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0


class DestroyAction(Action):
    pass


class UninterpretedAction(Action):
    pass


class AttributeLink(Core.ModelElement):

    class attribute(_model.StructuralFeature):
        referencedType = 'Foundation/Core/Attribute'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0

    class value(_model.StructuralFeature):
        referencedType = 'Instance'
        referencedEnd = 'attributeLink'
        upperBound = 1
        lowerBound = 1
        sortPosn = 1

    class instance(_model.StructuralFeature):
        referencedType = 'Instance'
        referencedEnd = 'slot'
        upperBound = 1
        lowerBound = 1
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
        referencedType = 'Foundation/Core/Association'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0

    class connection(_model.StructuralFeature):
        referencedType = 'LinkEnd'
        referencedEnd = 'link'
        isComposite = True
        lowerBound = 2
        sortPosn = 1

    class stimulus(_model.StructuralFeature):
        referencedType = 'Stimulus'
        referencedEnd = 'communicationLink'
        sortPosn = 2


class LinkObject(Object, Link):
    pass


class DataValue(Instance):
    pass


class CallAction(Action):

    class operation(_model.StructuralFeature):
        referencedType = 'Foundation/Core/Operation'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0


class SendAction(Action):

    class signal(_model.StructuralFeature):
        referencedType = 'Signal'
        referencedEnd = 'sendAction'
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
        referencedType = 'Foundation/Data_Types/Expression'
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
        referencedType = 'Foundation/Data_Types/String'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0

    class isRoot(_model.StructuralFeature):
        referencedType = 'Foundation/Data_Types/Boolean'
        upperBound = 1
        lowerBound = 1
        sortPosn = 1

    class isLeaf(_model.StructuralFeature):
        referencedType = 'Foundation/Data_Types/Boolean'
        upperBound = 1
        lowerBound = 1
        sortPosn = 2

    class isAbstract(_model.StructuralFeature):
        referencedType = 'Foundation/Data_Types/Boolean'
        upperBound = 1
        lowerBound = 1
        sortPosn = 3

    class signal(_model.StructuralFeature):
        referencedType = 'Signal'
        referencedEnd = 'reception'
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
        referencedType = 'Foundation/Core/AssociationEnd'
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
        referencedEnd = 'stimulus1'
        sortPosn = 0

    class sender(_model.StructuralFeature):
        referencedType = 'Instance'
        referencedEnd = 'stimulus3'
        upperBound = 1
        lowerBound = 1
        sortPosn = 1

    class receiver(_model.StructuralFeature):
        referencedType = 'Instance'
        referencedEnd = 'stimulus2'
        upperBound = 1
        lowerBound = 1
        sortPosn = 2

    class communicationLink(_model.StructuralFeature):
        referencedType = 'Link'
        referencedEnd = 'stimulus'
        upperBound = 1
        sortPosn = 3

    class dispatchAction(_model.StructuralFeature):
        referencedType = 'Action'
        referencedEnd = 'stimulus'
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

# ------------------------------------------------------------------------------

#_config.setupModule()


