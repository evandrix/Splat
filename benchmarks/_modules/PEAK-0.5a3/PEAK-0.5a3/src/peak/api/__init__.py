"""The Complete PEAK API (Core + Frameworks)

 This module is similar to 'peak.core', but also offers convenient lazy imports
 for all of PEAK's framework API's:

    'commands' -- Gives you access to 'peak.running.commands', a framework for
        command-line application components

    'logs' -- Gives you access to 'peak.running.logs', a logging framework
        that works with (or without) the PEP 282 logging package.

    'running' -- Gives you access to the 'peak.running.api', which provides
        frameworks for command line applications, lock files, event-driven
        applications, CGI, FastCGI, Unix child process management,
        and autonomous agents (periodic tasks).

    'security' -- Gives you access to the 'peak.security.api', which provides
        an extremely flexible rule-based access control system using abstract
        and concrete permissions, that can use context-dependent business rules
        to grant or deny permissions to principals.

    'storage' -- Gives you access to the 'peak.storage.api', which offers
        frameworks for transactions, persistence, and database access.

    'web' -- Gives you access to the 'peak.web.api', a framework for building
        adaptation-driven web applications atop the CGI/FastCGI framework
        provided by 'peak.running'.
"""

from peak.core import *
from peak.core import __all__

__all__ = __all__[:] + [
    'commands', 'events', 'logs', #'net', 'query',
    'running', 'security', 'storage', 'web',
]





# Convenience features
from peak.util.imports import lazyModule

commands    = lazyModule('peak.running.commands')
events      = lazyModule('peak.events.api')
logs        = lazyModule('peak.running.logs')
#net         = lazyModule('peak.net.api')
#query       = lazyModule('peak.query.api')
running     = lazyModule('peak.running.api')
security    = lazyModule('peak.security.api')
storage     = lazyModule('peak.storage.api')
web         = lazyModule('peak.web.api')


# This is here so that 'peak help iif' will return something useful.
# It is not actually exported from here!  'config.ini_files' imports it
# directly, so it'll be available from .ini files.

def iif(cond,Then,Else):
    """iif(cond,then,else) -- return 'then' if 'cond' is true, else 'else'"""
    if cond:
        return Then
    return Else


















