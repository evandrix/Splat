# ------------------------------------------------------------------------------
# Package: peak.metamodels.UML13.model.Behavioral_Elements
# File:    peak\metamodels\UML13\model\Behavioral_Elements\__init__.py
# ------------------------------------------------------------------------------

from peak.util.imports import lazyModule as _lazy

_model               = _lazy('peak.model.api')
#_config             = _lazy('peak.config.api')

Foundation           = _lazy(__name__, '../Foundation')
Common_Behavior      = _lazy(__name__, 'Common_Behavior')
Use_Cases            = _lazy(__name__, 'Use_Cases')
State_Machines       = _lazy(__name__, 'State_Machines')
Collaborations       = _lazy(__name__, 'Collaborations')
Activity_Graphs      = _lazy(__name__, 'Activity_Graphs')

# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------

#_config.setupModule()


