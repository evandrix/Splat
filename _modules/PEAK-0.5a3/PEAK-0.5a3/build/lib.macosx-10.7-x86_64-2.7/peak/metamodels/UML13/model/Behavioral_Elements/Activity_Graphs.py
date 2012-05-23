# ------------------------------------------------------------------------------
# Package: peak.metamodels.UML13.model.Behavioral_Elements.Activity_Graphs
# File:    peak\metamodels\UML13\model\Behavioral_Elements\Activity_Graphs.py
# ------------------------------------------------------------------------------

from peak.util.imports import lazyModule as _lazy

_model               = _lazy('peak.model.api')
#_config             = _lazy('peak.config.api')

State_Machines       = _lazy(__name__, '../State_Machines')
Core                 = _lazy(__name__, '../../Foundation/Core')

# ------------------------------------------------------------------------------


class ActivityGraph(State_Machines.StateMachine):

    class partition(_model.StructuralFeature):
        referencedType = 'Partition'
        referencedEnd = 'activityGraph'
        isComposite = True
        sortPosn = 0


class Partition(Core.ModelElement):

    class contents(_model.StructuralFeature):
        referencedType = 'Foundation/Core/ModelElement'
        sortPosn = 0

    class activityGraph(_model.StructuralFeature):
        referencedType = 'ActivityGraph'
        referencedEnd = 'partition'
        upperBound = 1
        lowerBound = 1
        sortPosn = 1


class SubactivityState(State_Machines.SubmachineState):

    class isDynamic(_model.StructuralFeature):
        referencedType = 'Foundation/Data_Types/Boolean'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0

    class dynamicArguments(_model.StructuralFeature):
        referencedType = 'Foundation/Data_Types/ArgListsExpression'
        upperBound = 1
        lowerBound = 1
        sortPosn = 1

    class dynamicMultiplicity(_model.StructuralFeature):
        referencedType = 'Foundation/Data_Types/Multiplicity'
        upperBound = 1
        lowerBound = 1
        sortPosn = 2


class ActionState(State_Machines.SimpleState):

    class isDynamic(_model.StructuralFeature):
        referencedType = 'Foundation/Data_Types/Boolean'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0

    class dynamicArguments(_model.StructuralFeature):
        referencedType = 'Foundation/Data_Types/ArgListsExpression'
        upperBound = 1
        lowerBound = 1
        sortPosn = 1

    class dynamicMultiplicity(_model.StructuralFeature):
        referencedType = 'Foundation/Data_Types/Multiplicity'
        upperBound = 1
        lowerBound = 1
        sortPosn = 2


class CallState(ActionState):
    pass


class ObjectFlowState(State_Machines.SimpleState):

    class isSynch(_model.StructuralFeature):
        referencedType = 'Foundation/Data_Types/Boolean'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0

    class parameter(_model.StructuralFeature):
        referencedType = 'Foundation/Core/Parameter'
        sortPosn = 1

    class type(_model.StructuralFeature):
        referencedType = 'Foundation/Core/Classifier'
        upperBound = 1
        lowerBound = 1
        sortPosn = 2


class ClassifierInState(Core.Classifier):

    class type(_model.StructuralFeature):
        referencedType = 'Foundation/Core/Classifier'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0

    class inState(_model.StructuralFeature):
        referencedType = 'State_Machines/State'
        lowerBound = 1
        sortPosn = 1

# ------------------------------------------------------------------------------

#_config.setupModule()


