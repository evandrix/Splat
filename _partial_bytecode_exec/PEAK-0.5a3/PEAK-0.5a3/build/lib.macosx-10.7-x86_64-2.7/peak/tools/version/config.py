from peak.api import *
from shlex import shlex
from cStringIO import StringIO
from peak.storage.files import EditableFile
from peak.util.FileParsing import AbstractConfigParser
from peak.util.imports import importObject
safe_globals = {'__builtins__':{}}


class IPartDef(protocols.Interface):

    name = protocols.Attribute(
        """Name of the part"""
    )

    independent = protocols.Attribute(
        """If true, part should not be reset when a parent is incremented"""
    )

    def incr(value):
        """Return the successor of value"""

    def reset(value):
        """Return the reset of value"""

    def asNumeral(value):
        """Return the value as a numeral (used for optional/remap formats)"""

    def validate(value):
        """Return the internal form of the string 'value', or raise error"""


class IFormat(protocols.Interface):

    def compute(version):
        """Return the formatted value of 'version' for this format"""





def tokenize(s):
    return list(iter(shlex(StringIO(s)).get_token,''))

def unquote(s):
    if s.startswith('"') or s.startswith("'"):
        s = s[1:-1]
    return s

PART_FACTORIES   = PropertyName('version-tool.partKinds')
FORMAT_FACTORIES = PropertyName('version-tool.formatKinds')































class Digit(binding.Component):

    protocols.advise(
        instancesProvide = [IPartDef]
    )

    name = binding.Require("Name of the part")

    def independent(self):
        for arg in self.args:
            if unquote(arg).lower()=='independent':
                return True
            else:
                raise ValueError(
                    "Unrecognized option %r in %r" % (arg,self.cmd)
                )
        return False

    independent = binding.Make(independent, suggestParent=False)

    start = 0
    args = ()
    cmd = ""

    def incr(self, value):
        return value+1

    def reset(self, value):
        return self.start

    def validate(self, value):
        return int(value)

    def asNumeral(self,value):
        return self.validate(value)


class Count(Digit):
    start = 1


class Choice(Digit):

    choices = binding.Make(
        lambda self: [unquote(arg) for arg in self.args]
    )

    choiceMap = binding.Make(
        lambda self: dict(
            zip([c.strip().lower() for c in self.choices],
                range(len(self.choices))
            )
        )
    )

    independent = False


    def incr(self, value):
        pos = self.choices.index(self.validate(value)) + 1
        if pos>=len(self.choices):
            raise ValueError("Can't increment %s past %r" % (self.name,value))
        return self.choices[pos]


    def reset(self, value):
        return self.choices[self.start]


    def asNumeral(self, value):
        value = value.lower().strip()
        try:
            return self.choiceMap[value]
        except KeyError:
            raise ValueError(
                "Invalid %s %r: must be one of %r" %
                (self.name, value, self.choices)
            )

    def validate(self, value):
        return self.choices[self.asNumeral(value)]

class Timestamp(Digit):

    independent = True

    def incr(self, value):
        from time import time
        return time()

    def reset(self, value):
        raise ValueError("Timestamp values don't reset") # XXX

    def asNumeral(self, value):
        return float(value)

    def validate(self, value):
        raise ValueError("Can't set timestamp values directly yet") # XXX

























class StringFormat(binding.Component):

    protocols.advise(
        instancesProvide = [IFormat]
    )

    args = ()
    cmd = ""
    name = binding.Require("Name of the format")

    def format(self):
        try:
            fmt, = self.args
        except ValueError:
            raise ValueError(
                "%s: missing or multiple format strings in %r" %
                (self.name, self.cmd)
            )
        else:
            return unquote(fmt)

    format = binding.Make(format)

    def compute(self, version):
        return self.format % version
















class Remap(StringFormat):

    scheme = binding.Obtain('..')

    def splitArgs(self):
        args = [unquote(arg) for arg in self.args]
        if not args:
            raise ValueError(
                "%s: remap without field name or values" % self.name
            )
        return args[0], args[1:]

    splitArgs = binding.Make(splitArgs)

    what = binding.Make(lambda self: self.splitArgs[0])
    fmts = binding.Make(lambda self: self.splitArgs[1])

    def compute(self, version):
        value = version[self.what]
        if self.what in self.scheme.partMap:
            value = self.scheme.partMap[self.what].asNumeral(value)
        return self.getFormat(value) % version

    def getFormat(self, value):
        try:
            return self.fmts[value]
        except IndexError:
            return ""













class Optional(Remap):

    def splitFormats(self):

        fmts = self.fmts

        if fmts:
            return (fmts+[''])[:1]

        # Default formats are the value or an empty string
        return ('%%(%s)s' % self.what), ''

    splitFormats = binding.Make(splitFormats)

    trueFormat = binding.Make(lambda self: self.splitFormats[0])
    falseFormat = binding.Make(lambda self: self.splitFormats[1])

    def getFormat(self, value):
        if value:
            return self.trueFormat
        return self.falseFormat




















class DateFormat(Remap):

    def format(self):

        try:
            fmt, = self.fmts
        except ValueError:
            raise ValueError(
                "%s: too many formats in %r" % (self.name, self.cmd)
            )
        return fmt

    format = binding.Make(format)

    def compute(self,version):
        from datetime import datetime
        value = datetime.fromtimestamp(version[self.what])
        return value.strftime(self.format)























class VersionStore(EditableFile, AbstractConfigParser):
    """Simple writable config file for version data"""

    txnAttrs = EditableFile.txnAttrs + ('parsedData',)

    def add_setting(self, section, name, value, lineInfo):
        self.data.setdefault(section,{})[name] = eval(
            value,safe_globals,{}
        )

    def parsedData(self):
        self.data = {}
        if self.text:
            self.readString(self.text, self.filename)
        return self.data

    parsedData = binding.Make(parsedData)

    def getVersion(self,name):
        try:
            return self.parsedData[name]
        except KeyError:
            raise ValueError(
                "Missing version info for %r in %s" % (name,self.filename)
            )

    def setVersion(self,name,data):
        self.parsedData[name] = data
        self.text = ''.join(
            [
                ("[%s]\n%s\n" %
                    (k,
                    ''.join(
                            [("%s = %r\n" % (kk,vv)) for kk,vv in v.items()]
                        )
                    )
                )
                for k,v in self.parsedData.items()
            ]
        )

class Scheme(binding.Component):

    name = binding.Obtain('_name')
    _name = None

    parts = binding.Make(
        lambda self: [self.makePart(txt) for txt in self.partDefs],
        doc = "IPartDefs of the versioning scheme"
    )

    formats = binding.Make(
        lambda self: dict(
            [(name,self.makeFormat(name,txt))
                for (name,txt) in self.formatDefs.items()
            ]
        ),
        doc = "dictionary of IFormat objects"
    )

    partDefs = binding.Require("list of part definition directives")
    formatDefs = binding.Require("dictionary of format directives")

    defaultFormat = None

    partMap = binding.Make(
        lambda self: dict([(part.name,part) for part in self.parts])
    )

    def __getitem__(self,key):
        try:
            return self.partMap[key]
        except KeyError:
            return self.formats[key]








    def incr(self,data,part):

        d = data.copy()
        partsIter = iter(self.parts)
        for p in partsIter:
            if p.name == part:
                d[part] = p.incr(d[part])
                break
        else:
            return d

        # Reset digits to the right of the incremented digit

        for p in partsIter:
            if not p.independent:
                d[p.name] = p.reset(d[p.name])

        return d


    def makePart(self, directive):

        args = tokenize(directive)
        partName = args.pop(0)

        if args:
            typeName = PropertyName.fromString(args.pop(0).lower())
        else:
            typeName = 'digit'

        factory = importObject(PART_FACTORIES.of(self).get(typeName,None))

        if factory is None:
            raise ValueError(
                "Unrecognized part kind %r in %r" % (typeName,directive)
            )
        return factory(self, name=partName, args = args, cmd=directive)




    def makeFormat(self, name, directive):

        args = tokenize(directive)
        format = args[0]
        if format != unquote(format):
            format = 'string'
        else:
            args.pop(0)
            format = PropertyName.fromString(format.lower())

        factory = importObject(FORMAT_FACTORIES.of(self).get(format,None))

        if factory is None:
            raise ValueError(
                "Unrecognized format kind %r in %r for format %r" %
                (format,directive,name)
            )
        return factory(self, name=name, args = args, cmd=directive)























class Version(binding.Component):

    data = _cache = binding.Make(dict)
    scheme = binding.Require("Versioning scheme")

    def __getitem__(self, key):
        cache = self._cache
        if key in cache:
            value = cache[key]
            if value is NOT_FOUND:
                raise ValueError("Recursive attempt to compute %r" % key)
            return cache[key]

        data = self.data
        if key in data:
            value = cache[key] = data[key]
            return value

        cache[key] = NOT_FOUND
        try:
            scheme = self.scheme
            if key in scheme.formats:
                value = cache[key] = scheme.formats[key].compute(self)
            return value
        except:
            del cache[key]
            raise

        raise KeyError, key


    def withIncr(self, part):
        return self.__class__(
            self.getParentComponent(), self.getComponentName(),
            data   = self.scheme.incr(self.data, part),
            scheme = self.scheme
        )




    def withParts(self, partItems):

        scheme = self.scheme
        data = self.data.copy()

        for k,v in partItems:
            if k in scheme.partDefs:
                data[k] = scheme[k].validate(v)
            else:
                raise KeyError("Version has no part %r" % k)

        return self.__class__(
            self.getParentComponent(), self.getComponentName(),
            data = data, scheme = scheme
        )


    def __cmp__(self, other):
        return cmp(self.data, other)

    def __str__(self):
        fmt = self.scheme.defaultFormat
        if fmt:
            return self[fmt]
        return '[%s]' % ', '.join(
            [('%s=%r' % (p.name, self[p.name])) for p in self.scheme.parts]
        )



def getFormats(section):
    return section.formats









class Module(binding.Component):

    """A versionable entity, comprising files that need version strings"""

    name = binding.Require('name of this module')
    editors = binding.Require('list of Editors to use')

    schemeName = 'default'
    schemeMap = binding.Obtain('../schemeMap')
    versionStore = binding.Obtain('../versionStore')

    def versionScheme(self):
        try:
            return self.schemeMap[self.schemeName.lower()]
        except KeyError:
            raise ValueError(
                "Unrecognized version scheme '%r'" % self.schemeName
            )
    versionScheme = binding.Make(versionScheme)

    currentVersion = binding.Make(
        lambda self:
            Version(
                scheme = self.versionScheme,
                data =   self.versionStore.getVersion(self.name)
            )
    )

    def setVersion(self, partItems):
        old = self.currentVersion
        new = old.withParts(partItems)
        self._editVersion(old,new)

    def incrVersion(self, part):
        old = self.currentVersion
        new = old.withIncr(part)
        self._editVersion(old,new)

    def checkFiles(self):
        self._editVersion(self.currentVersion, self.currentVersion)

    def _editVersion(self, old, new):
        for editor in self.editors:
            editor.editVersion(old,new)
        if old<>new:
            self.currentVersion = new
            self.versionStore.setVersion(self.name, new.data)




class Editor(binding.Component):

    """Thing that applies a set of edits to a set of files"""

    filenames = binding.Require('sequence of filenames to edit')

    files = binding.Make(
        lambda self: [EditableFile(self,f,filename=f) for f in self.filenames]
    )

    edits = edits2 = binding.Require('list of IEdit instances to apply')

    def editVersion(self, old, new):
        for file in self.files:
            text = file.text
            if text is None:
                raise ValueError("File %s does not exist" % file.filename)

            posn = 0
            buffer = []
            for edit in self.edits:
                posn = edit.editVersion(
                    text, posn, old, new, buffer.append, file.filename
                )

            buffer.append(text[posn:])
            file.text = ''.join(buffer)




class Match(binding.Component):

    """Thing that finds/updates version strings"""

    matchString = binding.Require('string to match')
    isOptional = False

    def editVersion(self, text, posn, old, new, write, filename):
        old = self.matchString % old
        new = self.matchString % new
        foundOld = text.find(old,posn)
        foundNew = text.find(new,posn)
        if foundOld==-1:
            if foundNew==-1:
                if self.isOptional:
                    return posn
                else:
                    raise ValueError(
                        "Couldn't find %r or %r in %s" % (old,new,filename)
                    )
            else:
                newPosn = foundNew + len(new)
                write(text[posn:newPosn])
                return newPosn
        else:
            write(text[posn:foundOld])
            write(new)
            newPosn = foundOld + len(old)
            return newPosn












    def fromString(klass, text):
        """ZConfig constructor for 'Match' operator"""

        args = tokenize(text)
        isOptional = (args[0].lower()=='optional')
        if isOptional:
            args.pop(0)

        if not args:
            raise ValueError("No match string defined in %r" % text)
        elif len(args)>1:
            raise ValueError("Too many match strings in %r" % args)

        text, = args

        return klass(matchString=unquote(text), isOptional=isOptional)

    fromString = classmethod(fromString)























