"""A 'peak.model' metamodel for manipulating UML models

    This package can be used directly as a 'metamodel' for a XMI 1.0
    'peak.storage.xmi.DM'.  To see the actual structure of the metamodel,
    see the enclosed 'peak.metamodels.UML14.model' package.

    When using this package, however, you can completely ignore the 'model'
    subpackage, and import directly from 'UML14'.  Keep in mind that due to
    the use of package inheritance, all subpackages/submodules of the 'model'
    subpackage also exist in 'UML14'.  So you can import
    'peak.metamodels.UML14.Model_Management' even though there is no
    'Model_Management.py' file in the 'UML14' directory.  You should *not*
    import items from the 'model' subpackage directly unless you wish to
    inherit from them without using the convenience extensions defined in
    the outer package.
"""

from peak.api import config

# Inherit from the generated code (for the __init__ module)
__bases__ = 'model',


# Define a submodule, 'UML14.Core', that has 'core_addons'
# patched into it:

config.declareModule(__name__, 'Core',
    patches = ('/peak/metamodels/core_addons',)
)

config.setupModule()

