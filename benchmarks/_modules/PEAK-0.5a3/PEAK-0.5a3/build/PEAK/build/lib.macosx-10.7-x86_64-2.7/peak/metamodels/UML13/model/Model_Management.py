# ------------------------------------------------------------------------------
# Package: peak.metamodels.UML13.model.Model_Management
# File:    peak\metamodels\UML13\model\Model_Management.py
# ------------------------------------------------------------------------------

from peak.util.imports import lazyModule as _lazy

_model               = _lazy('peak.model.api')
#_config             = _lazy('peak.config.api')

Foundation           = _lazy(__name__, '../Foundation')
Core                 = _lazy(__name__, '../Foundation/Core')

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
        referencedType = 'Foundation/Data_Types/Boolean'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0


class ElementImport(_model.Element):

    class visibility(_model.StructuralFeature):
        referencedType = 'Foundation/Data_Types/VisibilityKind'
        upperBound = 1
        lowerBound = 1
        sortPosn = 0

    class alias(_model.StructuralFeature):
        referencedType = 'Foundation/Data_Types/Name'
        upperBound = 1
        lowerBound = 1
        sortPosn = 1

    class package(_model.StructuralFeature):
        referencedType = 'Package'
        referencedEnd = 'elementImport'
        upperBound = 1
        lowerBound = 1
        sortPosn = 2

    class modelElement(_model.StructuralFeature):
        referencedType = 'Foundation/Core/ModelElement'
        upperBound = 1
        lowerBound = 1
        sortPosn = 3

# ------------------------------------------------------------------------------

#_config.setupModule()


