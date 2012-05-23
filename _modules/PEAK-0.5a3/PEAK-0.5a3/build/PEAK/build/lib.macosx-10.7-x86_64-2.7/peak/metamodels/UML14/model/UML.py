# ------------------------------------------------------------------------------
# Package: peak.metamodels.UML14.model.UML
# File:    peak\metamodels\UML14\model\UML.py
# ------------------------------------------------------------------------------

from peak.util.imports import lazyModule as _lazy

_model               = _lazy('peak.model.api')
#_config             = _lazy('peak.config.api')

Data_Types           = _lazy(__name__, '../Data_Types')
Core                 = _lazy(__name__, '../Core')
Common_Behavior      = _lazy(__name__, '../Common_Behavior')
Use_Cases            = _lazy(__name__, '../Use_Cases')
State_Machines       = _lazy(__name__, '../State_Machines')
Collaborations       = _lazy(__name__, '../Collaborations')
Activity_Graphs      = _lazy(__name__, '../Activity_Graphs')
Model_Management     = _lazy(__name__, '../Model_Management')

# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------

#_config.setupModule()


