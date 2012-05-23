"""API for Event-driven programming and co-operative multitasking"""

from interfaces import *
from sources import *
from event_threads import *

IS_TWISTED = 'peak.events.isTwisted'

def ifTwisted(ob,twistedValue,untwistedValue):
    """Return 'twistedValue' if 'ob' is in a Twisted service area"""

    from peak.api import config
    sa = config.parentProviding(ob, config.IServiceArea)

    if config.lookup(sa,IS_TWISTED,None):
        return twistedValue
    return untwistedValue


def makeTwisted(ob):
    """Try to make service area containing 'ob' a Twisted area"""

    from peak.api import config
    from peak.util.EigenData import AlreadyRead
    sa = config.parentProviding(ob, config.IServiceArea)

    try:
        sa.registerProvider(IS_TWISTED, config.Value(True))
    except AlreadyRead:
        pass

    if not config.lookup(sa,IS_TWISTED,None):
        raise AlreadyRead(
            "Another reactor is already in use for this service area"
        )

    return True

