__all__ = [
    'Persistent', 'PersistentMetaClass', 'isGhost'
]

# Ugh; this is the one place where relative imports are annoying:
# when you can't turn them off!

from peak.util.imports import importString

import __main__
md = __main__.__dict__

Persistent             = importString('persistence:Persistent', md)
PersistentMetaClass    = importString('persistence:PersistentMetaClass', md)
GHOST                  = importString('persistence._persistence:GHOST', md)
IPersistent            = importString('persistence.interfaces:IPersistent', md)
IPersistentDataManager = importString(
    'persistence.interfaces:IPersistentDataManager', md
)

def isGhost(obj):
    return obj._p_state == GHOST

try:
    import zope.interface
except ImportError:
    # For safety's sake, declare that Persistent implements IPersistent,
    # since the '__implements__' attribute it's using is useless if
    # 'zope.interface' isn't around.
    from protocols import declareImplementation
    declareImplementation(Persistent, instancesProvide=[IPersistent])
else:
    # Ensure we have support for Zope interfaces
    import protocols.zope_support
    
# XXX It's not clear that we should be using GHOST
# XXX do we need simple_new()?  What is it for, anyway?



