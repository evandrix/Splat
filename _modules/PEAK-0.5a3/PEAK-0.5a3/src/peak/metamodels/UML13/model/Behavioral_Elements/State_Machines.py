# ------------------------------------------------------------------------------
# Package: peak.metamodels.UML13.model.Behavioral_Elements.State_Machines
# File:    peak\metamodels\UML13\model\Behavioral_Elements\State_Machines.py
# ------------------------------------------------------------------------------

from peak.util.imports import lazyModule as _lazy

_model               = _lazy('peak.model.api')
#_config             = _lazy('peak.config.api')

Core                 = _lazy(__name__, '../../Foundation/Core')

# ------------------------------------------------------------------------------


class StateMachine(Core.ModelElement):

    class context(_model.StructuralFeature):
        referencedType = 'Foundation/Core/ModelElement'
        upperBound = 1
        sortPosn = 0

    class top(_model.StructuralFeature):
        referencedType = 'State'
        referencedEnd = 'stateMachine'
        isComposite = True
        upperBound = 1
        lowerBound = 1
        sortPosn = 1

    class transitions(_model.StructuralFeature):
        referencedType = 'Transition'
        referencedEnd = 'stateMachine'
        isComposite = True
        sortPosn = 2

    class subMachineState(_model.StructuralFeature):
        referencedType = 'SubmachineState'
        referencedEnd = 'submachine'
        sortPosn = 3


class Event(Core.ModelElement):

    mdl_isAbstract = True

    class parameter(_model.StructuralFeature):
        referencedType = 'Foundation/Core/Parameter'
        isComposite = True
        sortPosn = 0

    class state(_model.StructuralFeature):
        referencedType = 'State'
        referencedEnd = 'deferrableEvent'
        sortPosn = 1

    class transition(_model.StructuralFeature):
        referencedType = 'Transition'
        referencedEnd = 'trigger'
        sortPosn = 2


class StateVertex(Core.ModelElement):

    mdl_isAbstract = True

    class container(_model.StructuralFeature):
        referencedType = 'CompositeState'
        referencedEnd = 'subvertex'
        upperBound = 1
        sortPosn = 0

    class outgoing(_model.StructuralFeature):
        referencedType = 'Transition'
        referencedEnd = 'source'
        sortPosn = 1

    class incoming(_model.StructuralFeature):
        referencedType = 'Transition'
        referencedEnd = 'target'
        sortPosn = 2


class State(StateVertex):

    mdl_isAbstract = True

    class entry(_model.StructuralFeature):
        referencedType = 'Common_Behavior/Action'
        isComposite = True
        upperBound = 1
        sortPosn = 0

    class exit(_model.StructuralFeature):
        referencedType = 'Common_Behavior/Action'
        isComposite = True
        upperBound = 1
        sortPosn = 1

    class stateMachine(_model.StructuralFeature):
        referencedType = 'StateMachine'
        referencedEnd = 'top'
        upperBound = 1
        sortPosn = 2

    class deferrableEvent(_model.StructuralFeature):
        referencedType = 'Event'
        referencedEnd = 'state'
        sortPosn = 3

    class internalTransition(_model.StructuralFeature):
        referencedType = 'Transition'
        referencedEnd = 'state'
        isComposite = True
        sortPosn = 4

    class doActivity(_model.StructuralFeature):
        referencedType = 'Common_Behavior/Action'
        isComposite = True
        upperBound = 1
        sortPosn = 5


class TimeEvent(Event):

    class when(_model.StructuralFeature):
        referencedType = 'Foundation/Data_Types/TimeExpression'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0


class CallEvent(Event):

    class operation(_model.StructuralFeature):
        referencedType = 'Foundation/Core/Operation'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0


class SignalEvent(Event):

    class signal(_model.StructuralFeature):
        referencedType = 'Common_Behavior/Signal'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0


class Transition(Core.ModelElement):

    class guard(_model.StructuralFeature):
        referencedType = 'Guard'
        referencedEnd = 'transition'
        isComposite = True
        upperBound = 1
        sortPosn = 0

    class effect(_model.StructuralFeature):
        referencedType = 'Common_Behavior/Action'
        isComposite = True
        upperBound = 1
        sortPosn = 1

    class state(_model.StructuralFeature):
        referencedType = 'State'
        referencedEnd = 'internalTransition'
        upperBound = 1
        sortPosn = 2

    class trigger(_model.StructuralFeature):
        referencedType = 'Event'
        referencedEnd = 'transition'
        upperBound = 1
        sortPosn = 3

    class stateMachine(_model.StructuralFeature):
        referencedType = 'StateMachine'
        referencedEnd = 'transitions'
        upperBound = 1
        sortPosn = 4

    class source(_model.StructuralFeature):
        referencedType = 'StateVertex'
        referencedEnd = 'outgoing'
        upperBound = 1
        lowerBound = 1
        sortPosn = 5

    class target(_model.StructuralFeature):
        referencedType = 'StateVertex'
        referencedEnd = 'incoming'
        upperBound = 1
        lowerBound = 1
        sortPosn = 6


class CompositeState(State):

    class isConcurrent(_model.StructuralFeature):
        referencedType = 'Foundation/Data_Types/Boolean'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0

    class subvertex(_model.StructuralFeature):
        referencedType = 'StateVertex'
        referencedEnd = 'container'
        isComposite = True
        sortPosn = 1


class ChangeEvent(Event):

    class changeExpression(_model.StructuralFeature):
        referencedType = 'Foundation/Data_Types/BooleanExpression'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0


class Guard(Core.ModelElement):

    class expression(_model.StructuralFeature):
        referencedType = 'Foundation/Data_Types/BooleanExpression'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0

    class transition(_model.StructuralFeature):
        referencedType = 'Transition'
        referencedEnd = 'guard'
        upperBound = 1
        lowerBound = 1
        sortPosn = 1


class Pseudostate(StateVertex):

    class kind(_model.StructuralFeature):
        referencedType = 'Foundation/Data_Types/PseudostateKind'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0


class SimpleState(State):
    pass


class SubmachineState(CompositeState):

    class submachine(_model.StructuralFeature):
        referencedType = 'StateMachine'
        referencedEnd = 'subMachineState'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0


class SynchState(StateVertex):

    class bound(_model.StructuralFeature):
        referencedType = 'Foundation/Data_Types/UnlimitedInteger'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0


class StubState(StateVertex):

    class referenceState(_model.StructuralFeature):
        referencedType = 'Foundation/Data_Types/Name'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0


class FinalState(State):
    pass

# ------------------------------------------------------------------------------

#_config.setupModule()


