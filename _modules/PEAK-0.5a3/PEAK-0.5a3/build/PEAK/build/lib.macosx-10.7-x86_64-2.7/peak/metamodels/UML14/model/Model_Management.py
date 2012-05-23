# ------------------------------------------------------------------------------
# Package: peak.metamodels.UML14.model.Model_Management
# File:    peak\metamodels\UML14\model\Model_Management.py
# ------------------------------------------------------------------------------

from peak.util.imports import lazyModule as _lazy

_model               = _lazy('peak.model.api')
#_config             = _lazy('peak.config.api')

Data_Types           = _lazy(__name__, '../Data_Types')
Core                 = _lazy(__name__, '../Core')
Core                 = _lazy(__name__, '../Core')

# ------------------------------------------------------------------------------


class Package(Core.GeneralizableElement, Core.Namespace):

    class elementImport(_model.StructuralFeature):
        referencedType = 'ElementImport'
        referencedEnd = 'package'
        isComposite = True
        sortPosn = 0


class Model(Package):
    pass


class Subsystem(Package, Core.Classifier):

    class isInstantiable(_model.StructuralFeature):
        referencedType = 'Data_Types/Boolean'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0


class ElementImport(_model.Element):

    class visibility(_model.StructuralFeature):
        referencedType = 'Data_Types/VisibilityKind'
        upperBound = 1
        sortPosn = 0

    class alias(_model.StructuralFeature):
        referencedType = 'Data_Types/Name'
        upperBound = 1
        sortPosn = 1

    class isSpecification(_model.StructuralFeature):
        referencedType = 'Data_Types/Boolean'
        upperBound = 1
        lowerBound = 1
        sortPosn = 2

    class package(_model.StructuralFeature):
        referencedType = 'Package'
        referencedEnd = 'elementImport'
        upperBound = 1
        lowerBound = 1
        sortPosn = 3

    class importedElement(_model.StructuralFeature):
        referencedType = 'Core/ModelElement'
        upperBound = 1
        lowerBound = 1
        sortPosn = 4

# ------------------------------------------------------------------------------

#_config.setupModule()


