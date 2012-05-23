from peak.api import *

class IN2Interactor(protocols.Interface):
    """An object that the user can interact with"""
    
    def interact(object, n2):
        """Allow the user to interact with the object"""
