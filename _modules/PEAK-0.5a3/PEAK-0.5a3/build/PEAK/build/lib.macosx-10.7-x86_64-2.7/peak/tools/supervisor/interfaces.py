from peak.api import *
from protocols import Interface

__all__ = ['ISupervisorPluginProvider']

class ISupervisorPluginProvider(running.IProcessTemplate):
    """Process template that also provides plugins for a supervisor process"""

    def getSupervisorPlugins(supervisor):
        """Return a sequence of plugins for 'supervisor' to use"""


