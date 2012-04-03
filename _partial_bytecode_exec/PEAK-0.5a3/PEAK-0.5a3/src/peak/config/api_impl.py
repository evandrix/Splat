"""Configuration Management API"""

from peak.api import exceptions, NOT_FOUND, NOT_GIVEN, PropertyName, adapt
from interfaces import *
from config_components import lookup, ConfigurationRoot, Value, parentProviding


__all__ = [
    'getProperty', 'setPropertyFor', 'setRuleFor', 'setDefaultFor', #DEPRECATED
    'makeRoot',
]


def setPropertyFor(obj, propName, value):
    """DEPRECATED"""
    parentProviding(obj, IConfigurable).registerProvider(
        propName, Value(value)
    )


def setRuleFor(obj, propName, ruleObj):
    """DEPRECATED"""
    parentProviding(obj, IConfigurable).registerProvider(propName, ruleObj)


def setDefaultFor(obj, propName, defaultObj):
    """DEPRECATED"""
    parentProviding(obj, IConfigurable).registerProvider(
        PropertyName(propName+'?'), defaultObj
    )











def makeRoot(**options):

    """Create a configuration root, suitable for use as a parent component

    This creates and returns a new 'IConfigurationRoot' with its default
    configuration loading from 'peak.ini'.  The returned root component
    will "know" it is a root, so any components that use it as a parent
    will get their 'uponAssembly()' events invoked immediately.

    Normally, this function is called without any parameters, but it will
    also accept keyword arguments that it will pass along when it calls the
    'peak.config.config_components.ConfigurationRoot' constructor.

    Currently, the only acceptable keyword argument is 'iniFiles', which must
    be a sequence of filename strings or '(moduleName,fileName)' tuples.

    The default value of 'iniFiles' is '[("peak","peak.ini")]', which loads
    useful system defaults from 'peak.ini' in the 'peak' package directory.
    Files are loaded in the order specified, with later files overriding
    earlier ones, unless the setting to be overridden has already been used
    (in which case an 'AlreadyRead' error occurs)."""

    return ConfigurationRoot(None, **options)


def getProperty(obj, propName, default=NOT_GIVEN):

    """DEPRECATED: use 'config.lookup()' instead"""
    return lookup(obj, propName, default)












