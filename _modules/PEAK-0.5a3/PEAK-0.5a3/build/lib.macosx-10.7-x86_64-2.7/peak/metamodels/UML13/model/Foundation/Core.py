# ------------------------------------------------------------------------------
# Package: peak.metamodels.UML13.model.Foundation.Core
# File:    peak\metamodels\UML13\model\Foundation\Core.py
# ------------------------------------------------------------------------------

from peak.util.imports import lazyModule as _lazy

_model               = _lazy('peak.model.api')
#_config             = _lazy('peak.config.api')


# ------------------------------------------------------------------------------


class Element(_model.Element):

    mdl_isAbstract = True


class ModelElement(Element):

    mdl_isAbstract = True

    class name(_model.StructuralFeature):
        referencedType = 'Data_Types/Name'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0

    class visibility(_model.StructuralFeature):
        referencedType = 'Data_Types/VisibilityKind'
        upperBound = 1
        lowerBound = 1
        sortPosn = 1

    class isSpecification(_model.StructuralFeature):
        referencedType = 'Data_Types/Boolean'
        upperBound = 1
        lowerBound = 1
        sortPosn = 2

    class namespace(_model.StructuralFeature):
        referencedType = 'Namespace'
        referencedEnd = 'ownedElement'
        upperBound = 1
        sortPosn = 3

    class clientDependency(_model.StructuralFeature):
        referencedType = 'Dependency'
        referencedEnd = 'client'
        sortPosn = 4

    class constraint(_model.StructuralFeature):
        referencedType = 'Constraint'
        referencedEnd = 'constrainedElement'
        sortPosn = 5

    class supplierDependency(_model.StructuralFeature):
        referencedType = 'Dependency'
        referencedEnd = 'supplier'
        sortPosn = 6

    class presentation(_model.StructuralFeature):
        referencedType = 'PresentationElement'
        referencedEnd = 'subject'
        sortPosn = 7

    class targetFlow(_model.StructuralFeature):
        referencedType = 'Flow'
        referencedEnd = 'target'
        sortPosn = 8

    class sourceFlow(_model.StructuralFeature):
        referencedType = 'Flow'
        referencedEnd = 'source'
        sortPosn = 9

    class templateParameter3(_model.StructuralFeature):
        referencedType = 'TemplateParameter'
        referencedEnd = 'defaultElement'
        sortPosn = 10

    class binding(_model.StructuralFeature):
        referencedType = 'Binding'
        referencedEnd = 'argument'
        upperBound = 1
        sortPosn = 11

    class comment(_model.StructuralFeature):
        referencedType = 'Comment'
        referencedEnd = 'annotatedElement'
        sortPosn = 12

    class elementResidence(_model.StructuralFeature):
        referencedType = 'ElementResidence'
        referencedEnd = 'resident'
        sortPosn = 13

    class templateParameter(_model.StructuralFeature):
        referencedType = 'TemplateParameter'
        referencedEnd = 'modelElement'
        isComposite = True
        sortPosn = 14

    class templateParameter2(_model.StructuralFeature):
        referencedType = 'TemplateParameter'
        referencedEnd = 'modelElement2'
        sortPosn = 15


class GeneralizableElement(ModelElement):

    mdl_isAbstract = True

    class isRoot(_model.StructuralFeature):
        referencedType = 'Data_Types/Boolean'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0

    class isLeaf(_model.StructuralFeature):
        referencedType = 'Data_Types/Boolean'
        upperBound = 1
        lowerBound = 1
        sortPosn = 1

    class isAbstract(_model.StructuralFeature):
        referencedType = 'Data_Types/Boolean'
        upperBound = 1
        lowerBound = 1
        sortPosn = 2

    class generalization(_model.StructuralFeature):
        referencedType = 'Generalization'
        referencedEnd = 'child'
        sortPosn = 3

    class specialization(_model.StructuralFeature):
        referencedType = 'Generalization'
        referencedEnd = 'parent'
        sortPosn = 4


class Namespace(ModelElement):

    mdl_isAbstract = True

    class ownedElement(_model.StructuralFeature):
        referencedType = 'ModelElement'
        referencedEnd = 'namespace'
        isComposite = True
        sortPosn = 0


class Classifier(GeneralizableElement, Namespace):

    mdl_isAbstract = True

    class feature(_model.StructuralFeature):
        referencedType = 'Feature'
        referencedEnd = 'owner'
        isComposite = True
        sortPosn = 0

    class participant(_model.StructuralFeature):
        referencedType = 'AssociationEnd'
        referencedEnd = 'specification'
        sortPosn = 1

    class powertypeRange(_model.StructuralFeature):
        referencedType = 'Generalization'
        referencedEnd = 'powertype'
        sortPosn = 2


class Class(Classifier):

    class isActive(_model.StructuralFeature):
        referencedType = 'Data_Types/Boolean'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0


class DataType(Classifier):
    pass


class Feature(ModelElement):

    mdl_isAbstract = True

    class ownerScope(_model.StructuralFeature):
        referencedType = 'Data_Types/ScopeKind'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0

    class owner(_model.StructuralFeature):
        referencedType = 'Classifier'
        referencedEnd = 'feature'
        upperBound = 1
        sortPosn = 1


class StructuralFeature(Feature):

    mdl_isAbstract = True

    class multiplicity(_model.StructuralFeature):
        referencedType = 'Data_Types/Multiplicity'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0

    class changeability(_model.StructuralFeature):
        referencedType = 'Data_Types/ChangeableKind'
        upperBound = 1
        lowerBound = 1
        sortPosn = 1

    class targetScope(_model.StructuralFeature):
        referencedType = 'Data_Types/ScopeKind'
        upperBound = 1
        lowerBound = 1
        sortPosn = 2

    class type(_model.StructuralFeature):
        referencedType = 'Classifier'
        upperBound = 1
        lowerBound = 1
        sortPosn = 3


class AssociationEnd(ModelElement):

    class isNavigable(_model.StructuralFeature):
        referencedType = 'Data_Types/Boolean'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0

    class ordering(_model.StructuralFeature):
        referencedType = 'Data_Types/OrderingKind'
        upperBound = 1
        lowerBound = 1
        sortPosn = 1

    class aggregation(_model.StructuralFeature):
        referencedType = 'Data_Types/AggregationKind'
        upperBound = 1
        lowerBound = 1
        sortPosn = 2

    class targetScope(_model.StructuralFeature):
        referencedType = 'Data_Types/ScopeKind'
        upperBound = 1
        lowerBound = 1
        sortPosn = 3

    class multiplicity(_model.StructuralFeature):
        referencedType = 'Data_Types/Multiplicity'
        upperBound = 1
        lowerBound = 1
        sortPosn = 4

    class changeability(_model.StructuralFeature):
        referencedType = 'Data_Types/ChangeableKind'
        upperBound = 1
        lowerBound = 1
        sortPosn = 5

    class association(_model.StructuralFeature):
        referencedType = 'Association'
        referencedEnd = 'connection'
        upperBound = 1
        lowerBound = 1
        sortPosn = 6

    class qualifier(_model.StructuralFeature):
        referencedType = 'Attribute'
        referencedEnd = 'associationEnd'
        isComposite = True
        sortPosn = 7

    class type(_model.StructuralFeature):
        referencedType = 'Classifier'
        upperBound = 1
        lowerBound = 1
        sortPosn = 8

    class specification(_model.StructuralFeature):
        referencedType = 'Classifier'
        referencedEnd = 'participant'
        sortPosn = 9


class Interface(Classifier):
    pass


class Constraint(ModelElement):

    class body(_model.StructuralFeature):
        referencedType = 'Data_Types/BooleanExpression'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0

    class constrainedElement(_model.StructuralFeature):
        referencedType = 'ModelElement'
        referencedEnd = 'constraint'
        sortPosn = 1


class Relationship(ModelElement):

    mdl_isAbstract = True


class Association(GeneralizableElement, Relationship):

    class connection(_model.StructuralFeature):
        referencedType = 'AssociationEnd'
        referencedEnd = 'association'
        isComposite = True
        lowerBound = 2
        sortPosn = 0


class Attribute(StructuralFeature):

    class initialValue(_model.StructuralFeature):
        referencedType = 'Data_Types/Expression'
        upperBound = 1
        sortPosn = 0

    class associationEnd(_model.StructuralFeature):
        referencedType = 'AssociationEnd'
        referencedEnd = 'qualifier'
        upperBound = 1
        sortPosn = 1


class BehavioralFeature(Feature):

    mdl_isAbstract = True

    class isQuery(_model.StructuralFeature):
        referencedType = 'Data_Types/Boolean'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0

    class parameter(_model.StructuralFeature):
        referencedType = 'Parameter'
        referencedEnd = 'behavioralFeature'
        isComposite = True
        sortPosn = 1


class Operation(BehavioralFeature):

    class concurrency(_model.StructuralFeature):
        referencedType = 'Data_Types/CallConcurrencyKind'
        upperBound = 1
        lowerBound = 1
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

    class specification(_model.StructuralFeature):
        referencedType = 'Data_Types/String'
        upperBound = 1
        lowerBound = 1
        sortPosn = 4

    class method(_model.StructuralFeature):
        referencedType = 'Method'
        referencedEnd = 'specification'
        sortPosn = 5


class Parameter(ModelElement):

    class defaultValue(_model.StructuralFeature):
        referencedType = 'Data_Types/Expression'
        upperBound = 1
        sortPosn = 0

    class kind(_model.StructuralFeature):
        referencedType = 'Data_Types/ParameterDirectionKind'
        upperBound = 1
        lowerBound = 1
        sortPosn = 1

    class behavioralFeature(_model.StructuralFeature):
        referencedType = 'BehavioralFeature'
        referencedEnd = 'parameter'
        upperBound = 1
        sortPosn = 2

    class type(_model.StructuralFeature):
        referencedType = 'Classifier'
        upperBound = 1
        lowerBound = 1
        sortPosn = 3


class Method(BehavioralFeature):

    class body(_model.StructuralFeature):
        referencedType = 'Data_Types/ProcedureExpression'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0

    class specification(_model.StructuralFeature):
        referencedType = 'Operation'
        referencedEnd = 'method'
        upperBound = 1
        lowerBound = 1
        sortPosn = 1


class Generalization(Relationship):

    class discriminator(_model.StructuralFeature):
        referencedType = 'Data_Types/Name'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0

    class child(_model.StructuralFeature):
        referencedType = 'GeneralizableElement'
        referencedEnd = 'generalization'
        upperBound = 1
        lowerBound = 1
        sortPosn = 1

    class parent(_model.StructuralFeature):
        referencedType = 'GeneralizableElement'
        referencedEnd = 'specialization'
        upperBound = 1
        lowerBound = 1
        sortPosn = 2

    class powertype(_model.StructuralFeature):
        referencedType = 'Classifier'
        referencedEnd = 'powertypeRange'
        upperBound = 1
        sortPosn = 3


class AssociationClass(Association, Class):
    pass


class Dependency(Relationship):

    class client(_model.StructuralFeature):
        referencedType = 'ModelElement'
        referencedEnd = 'clientDependency'
        lowerBound = 1
        sortPosn = 0

    class supplier(_model.StructuralFeature):
        referencedType = 'ModelElement'
        referencedEnd = 'supplierDependency'
        lowerBound = 1
        sortPosn = 1


class Abstraction(Dependency):

    class mapping(_model.StructuralFeature):
        referencedType = 'Data_Types/MappingExpression'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0


class PresentationElement(Element):

    mdl_isAbstract = True

    class subject(_model.StructuralFeature):
        referencedType = 'ModelElement'
        referencedEnd = 'presentation'
        sortPosn = 0


class Usage(Dependency):
    pass


class Binding(Dependency):

    class argument(_model.StructuralFeature):
        referencedType = 'ModelElement'
        referencedEnd = 'binding'
        lowerBound = 1
        sortPosn = 0


class Component(Classifier):

    class deploymentLocation(_model.StructuralFeature):
        referencedType = 'Node'
        referencedEnd = 'resident'
        sortPosn = 0

    class residentElement(_model.StructuralFeature):
        referencedType = 'ElementResidence'
        referencedEnd = 'implementationLocation'
        isComposite = True
        sortPosn = 1


class Node(Classifier):

    class resident(_model.StructuralFeature):
        referencedType = 'Component'
        referencedEnd = 'deploymentLocation'
        sortPosn = 0


class Permission(Dependency):
    pass


class Comment(ModelElement):

    class annotatedElement(_model.StructuralFeature):
        referencedType = 'ModelElement'
        referencedEnd = 'comment'
        sortPosn = 0


class Flow(Relationship):

    class target(_model.StructuralFeature):
        referencedType = 'ModelElement'
        referencedEnd = 'targetFlow'
        sortPosn = 0

    class source(_model.StructuralFeature):
        referencedType = 'ModelElement'
        referencedEnd = 'sourceFlow'
        sortPosn = 1


class ElementResidence(_model.Element):

    class visibility(_model.StructuralFeature):
        referencedType = 'Data_Types/VisibilityKind'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0

    class resident(_model.StructuralFeature):
        referencedType = 'ModelElement'
        referencedEnd = 'elementResidence'
        upperBound = 1
        lowerBound = 1
        sortPosn = 1

    class implementationLocation(_model.StructuralFeature):
        referencedType = 'Component'
        referencedEnd = 'residentElement'
        upperBound = 1
        lowerBound = 1
        sortPosn = 2


class TemplateParameter(_model.Element):

    class defaultElement(_model.StructuralFeature):
        referencedType = 'ModelElement'
        referencedEnd = 'templateParameter3'
        upperBound = 1
        sortPosn = 0

    class modelElement(_model.StructuralFeature):
        referencedType = 'ModelElement'
        referencedEnd = 'templateParameter'
        upperBound = 1
        sortPosn = 1

    class modelElement2(_model.StructuralFeature):
        referencedType = 'ModelElement'
        referencedEnd = 'templateParameter2'
        upperBound = 1
        lowerBound = 1
        sortPosn = 2

# ------------------------------------------------------------------------------

#_config.setupModule()


