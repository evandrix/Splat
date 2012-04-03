"""A 'peak.model' metamodel for manipulating UML models

    This package can be used directly as a 'metamodel' for a
    'peak.storage.xmi.DM'.  To see the actual structure of the metamodel,
    see the enclosed 'peak.metamodels.UML13.model' package.

    When using this package, however, you can completely ignore the 'model'
    subpackage, and import directly from 'UML13'.  Keep in mind that due to
    the use of package inheritance, all subpackages/submodules of the 'model'
    subpackage also exist in 'UML13'.  So you can import
    'peak.metamodels.UML13.Model_Management' even though there is no
    'Model_Management.py' file in the 'UML13' directory.  You should *not*
    import items from the 'model' subpackage directly unless you wish to
    inherit from them without using the convenience extensions defined in
    the outer package.
"""

from peak.api import config

# Inherit from the generated code (for the __init__ module)
__bases__ = 'model',


# Define a submodule, 'UML13.Foundation.Core', that has 'core_addons'
# patched into it:

config.declareModule(__name__, 'Foundation/Core',
    patches = ('/peak/metamodels/core_addons',)
)

config.setupModule()

