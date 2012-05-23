# ------------------------------------------------------------------------------
# Package: peak.metamodels.UML13.model.Foundation
# File:    peak\metamodels\UML13\model\Foundation\__init__.py
# ------------------------------------------------------------------------------

from peak.util.imports import lazyModule as _lazy

_model               = _lazy('peak.model.api')
#_config             = _lazy('peak.config.api')

Data_Types           = _lazy(__name__, 'Data_Types')
Core                 = _lazy(__name__, 'Core')
Extension_Mechanisms = _lazy(__name__, 'Extension_Mechanisms')

# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------

#_config.setupModule()


