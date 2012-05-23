from peak.api import *
from peak.util.imports import importString, importObject, whenImported
from peak.util.FileParsing import AbstractConfigParser
from interfaces import *
from config_components import FactoryFor, CreateViaFactory, LazyRule, Value
import re; from peak.api import iif

__all__ = [
    'ConfigReader', 'loadConfigFiles', 'loadConfigFile', 'loadMapping',
    'ruleForExpr',
]

SECTION_PARSERS = PropertyName('peak.config.iniFile.sectionParsers')
CONFIG_LOADERS  = PropertyName('peak.config.loaders')
isIdentifier = re.compile('^[A-Za-z_][A-Za-z0-9_]*$').match

def ruleForExpr(name,expr,globalDict):
    """Return 'config.IRule' for property 'name' based on 'expr' string"""

    _ruleName = PropertyName(name)
    _rulePrefix = _ruleName.asPrefix()
    _lrp = len(_rulePrefix)

    def f(propertyMap, configKey, targetObj):
        ruleName = _ruleName
        rulePrefix = _rulePrefix
        if isinstance(configKey,PropertyName):
            propertyName = configKey
            ruleSuffix = propertyName[_lrp:]
        result = eval(expr,globalDict,locals())
        rule = adapt(result,ISmartProperty,None)
        if rule is not None:
            result = rule.computeProperty(
                propertyMap, propertyName, rulePrefix, ruleSuffix,
                targetObj
            )
        return result

    protocols.adviseObject(f,provides=[IRule])
    return f

def loadMapping(cMap, mapping, prefix='*', includedFrom=None):

    prefix = PropertyName(prefix).asPrefix()

    for k,v in mapping.items():
        cMap.registerProvider(PropertyName.fromString(prefix+k),Value(v))

protocols.adviseObject(loadMapping, provides=[ISettingLoader])


def loadConfigFile(pMap, filename, prefix='*', includedFrom=None):
    globalDict = getattr(includedFrom,'gloablDict',None)
    if filename:
        ConfigReader(pMap,prefix,globalDict).readFile(filename)

protocols.adviseObject(loadConfigFile, provides=[ISettingLoader])


def loadConfigFiles(pMap, filenames, prefix='*', includedFrom=None):

    if not filenames:
        return

    import os.path

    globalDict = getattr(includedFrom,'gloablDict',None)

    for filename in filenames:
        if filename and os.path.exists(filename):
            ConfigReader(pMap,prefix,globalDict).readFile(filename)

protocols.adviseObject(loadConfigFiles, provides=[ISettingLoader])









class ConfigReader(AbstractConfigParser):

    protocols.advise(
        instancesProvide=[IIniParser]
    )

    def __init__(self, propertyMap, prefix='*', globalDict=None):
        self.pMap = propertyMap
        self.prefix = PropertyName(prefix).asPrefix()
        if globalDict is None:
            globalDict = globals()
        self.globalDict = globalDict

    def add_setting(self, section, name, value, lineInfo):
        _ruleName = PropertyName(section+name)

        self.pMap.registerProvider(
            _ruleName,
            ruleForExpr(_ruleName,value,self.globalDict)
        )

    def add_section(self, section, lines, lineInfo):

        if section is None:
            section='*'

        section = section.strip()
        s = ' '.join(section.lower().split())

        if ' ' in s:
            pn = PropertyName.fromString(s.replace(' ','.'))
            func = importObject(SECTION_PARSERS.of(self.pMap).get(pn))
            if func is None:
                raise SyntaxError(("Invalid section type", section, lineInfo))
            handler = lambda *args: func(self, *args)
        else:
            section = self.prefix + PropertyName(section).asPrefix()
            handler = self.add_setting

        self.process_settings(section, lines, handler)

    def add_global(self,name,value):

        """Add/update a global variable for rules evaluation

        This creates a new 'globalDict' attribute, so that rules
        parsed before this global was added, will still be using
        the globals that were in effect when the rule was parsed."""

        self.globalDict = self.globalDict.copy()
        self.globalDict[name]=value



def do_include(parser, section, name, value, lineInfo):
    propertyMap = parser.pMap
    loader = importObject(CONFIG_LOADERS.of(propertyMap)[name])
    eval(
        "loader(propertyMap,%s,includedFrom=parser)" % value,
        parser.globalDict,
        locals()
    )


def register_factory(parser, section, name, value, lineInfo):
    module = '.'.join(name.replace(':','.').split('.')[:-1])
    pMap = parser.pMap
    globalDict = parser.globalDict

    def onImport(module):
        iface = importString(name)
        pMap.registerProvider(
            FactoryFor(iface),
            ruleForExpr(name,"importObject(%s)" % value, globalDict)
        )
        pMap.registerProvider(iface, CreateViaFactory(iface))

    whenImported(module, onImport)




def add_services(parser, section, name, value, lineInfo):
    name = PropertyName(name)
    pMap = parser.pMap
    globalDict = parser.globalDict
    factory = ruleForExpr(name, value, globalDict)
    pMap.registerProvider(
        FactoryFor(name), Value(lambda: factory(pMap,name,pMap))
    )
    pMap.registerProvider(name, CreateViaFactory(name))


def import_on_demand(parser, section, name, value, lineInfo):

    if not isIdentifier(name):
        e = SyntaxError(
            "%r is not a valid module shortcut name (at line %d in %s)" %
            (name,lineInfo[1],lineInfo[0])
        )
        e.filename, e.lineno, e.text = lineInfo
        raise e

    globalDict = parser.globalDict.copy()
    from peak.util.imports import lazyModule  # ensure it's in locals
    parser.add_global(name, eval("lazyModule(%s)" % value,globalDict,locals()))


def load_on_demand(parser, section, name, value, lineInfo):
    globalDict = parser.globalDict
    parser.pMap.registerProvider(
        PropertyName(name),
        LazyRule(
            lambda propertyMap, ruleName, propertyName: eval(value,globalDict,locals()),
            prefix = name
        )
    )






def provide_utility(parser, section, name, value, lineInfo):    # DEPRECATED!
    module = '.'.join(name.replace(':','.').split('.')[:-1])
    pMap = parser.pMap
    globalDict = parser.globalDict
    whenImported(
        module,
        lambda x: pMap.registerProvider(
            importString(name), eval(value,globalDict,locals())
        )
    )































