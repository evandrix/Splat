"""Module Inheritance and Patching

    The APIs defined here let you create modules which derive from other
    modules, by defining a module-level '__bases__' attribute which lists
    the modules you wish to inherit from.  For example::

        from peak.api import *

        import BaseModule1, BaseModule2

        __bases__ = BaseModule1, BaseModule2


        class MyClass:
            ...

        binding.setupModule()

    The 'setupModule()' call will convert the calling module, 'BaseModule1',
    and 'BaseModule2' into specially altered bytecode objects and execute
    them (in "method-resolution order") rewriting the calling module's
    dictionary in the process.  The result is rather like normal class
    inheritance, except that classes (even nested classes) are merged by name,
    and metaclass constraints are inherited.  So an inheriting module need
    not list all the classes from its base module in order to change them
    by altering a base class in that module.

    Note: All the modules listed in '__bases__' must either call
    'setupModule()' themselves, or be located in an on-disk '.py', '.pyc', or
    '.pyo' file.  This is because PEAK cannot otherwise get access to
    their bytecode in a way that is compatible with the many "import hook"
    systems that exist for Python.  (E.g. running bytecode from zip files or
    frozen into an executable, etc.)  So if you are using such a code
    distribution technique, you must ensure that the base modules call
    'setupModule()', even if they do not have a '__bases__' setting or use
    any other PEAK code.

    Function Rebinding

        All functions inherited via "module inheritance" using 'setupModule()'
        (including those which are instance or class methods) have their
        globals rebound to point to the inheriting module.  This means that if
        a function or method references a global in the base module you're
        inheriting from, you can override that global in the inheriting module,
        without having to recode the function that referenced it.  (This is
        especially useful for 'super()' calls, which usually use global
        references to class names!)

        In addition to rebinding general globals, functions which reference
        the global name '__proceed__' are also specially rebound so that
        '__proceed__' is the previous definition of that function, if any, in
        the inheritance list.  (It is 'None' if there is no previous
        definition.)  This allows you to do the rough equivalent of a 'super()'
        call (or AspectJ "around advice") without having to explicitly import
        the old version of a function.  Note that '__proceed__' is always
        either a function or 'None', so you must include 'self' as a parameter
        when calling it from a method definition.


    Pickling Instances of Nested Classes and the '__name__' Attribute

        One more bonus of using 'setupModule()' is that instances of nested
        classes defined in modules using 'setupModule()' will be pickleable.
        Ordinarily, nested class instances aren't pickleable because Python
        doesn't know how to find them, using only 'someClass.__name__' and
        'someClass.__module__'.

        PEAK overcomes this problem by renaming nested classes so that
        they are defined with their full dotted name (e.g. 'Foo.Bar' for
        class 'Bar' nested in class 'Foo'), and saving a reference to the class
        under its dotted name in the module dictionary.  This means that
        'someClass.__name__' may not be what you'd normally expect, and that
        doing 'del someClass' may not delete all references to a class.  But
        pickling and unpickling should work normally.

        Note that some PEAK classes and metaclasses provide a "short
        form" of the class name for use when appropriate.  For example,
        Feature classes have an 'attrName' class attribute.  In a pinch, you
        can also use '__name__.split(".")[-1]' to get the undotted form of
        a class' name.


    Special Considerations for Mutables and Dynamic Initialization

        Both inheritance and patching are implemented by running hacked,
        module-level code under a "simulator" that intercepts the setting of
        variables.  This works great for static definitions like 'class'
        and 'def' statements, constant assignments, 'import', etc.  It also
        works reasonably well for many other kinds of static initialization
        of immutable objects

        Mutable values, however, may require special considerations.  For
        example, if a module sets up some kind of registry as a module-level
        variable, and an inheriting module overrides the definition, things
        can get tricky.  If the base module writes values into that registry as
        part of module initialization, those values will also be written into
        the registry defined by the derived module.

        Another possible issue is if the base module performs other externally
        visible, non-idempotent operations, such as registering classes or
        functions in another module's registry, printing things to the console,
        etc.  The simple workaround for all these considerations, however, is
        to move your dynamic initialization code to a module-level '__init__'
        function.

    Module-level '__init__()' Functions

        The last thing 'setupModule()' does before returning, is to check for a
        module-level '__init__()' function, and call it with no arguments, if
        it exists.  This allows you to do any dynamic initialization operations
        (such as modifying or resetting global mutables) *after* inheritance
        has taken effect.  As with any other function defined in the module,
        '__proceed__' refers to the previous (i.e. preceding base module)
        definition of the function or 'None'.  This lets you can chain to your
        predecessors' initialization code, if needed/desired.

        Note, by the way, that if you have an 'if __name__=="__main__"' block
        in your module, it would probably be best if you move it inside the
        '__init__()' function, as this ensures that it will not be run
        repeatedly if you do not wish it to be.  It will also allow other
        modules to inherit that code and wrap around it, if they so desire.


    Package Inheritance

        Packages (i.e. '__init__' modules) can also set '__bases__' and
        call 'setupModule()'.  Their package '__path__' will be extended
        to include the '__path__' contents of their '__bases__', in an
        MRO-like order.  This means that to derive a package from another,
        you do not need to create a separate inheriting module for every
        individual module or subpackage, only those that you wish to make
        modifications to.  If package 'foo' contains modules 'foo.bar'
        and 'foo.baz', and you want your 'spam' package to derive from
        'foo', you need only create a 'spam/__init__.py' that contains::

            import foo
            __bases__ = foo,

            # ...

            from peak.api import config
            config.setupModule()

        At this point, 'spam.baz' or 'spam.bar' will automatically be
        importable, based on the 'foo' versions of their code.  This
        will work even if the 'foo' versions don't call 'setupModule()',
        although in that case you won't be able to override their contents.

        To override a module within the 'spam' package, just create it,
        and use module inheritance to specify the base in the original
        package.  For example, you can extend 'foo.bar' by creating
        'spam.bar' as follows::

            import foo.bar
            __bases__ = foo.bar,

            # ...

            from peak.api import config
            config.setupModule()




    Limitations of Package Inheritance

        Because "package inheritance" is effectively just a '__path__' hack,
        it is really only good for "single inheritance".  Python will not
        automatically merge the modules or packages found on a package's
        '__path__'.  So if you need multiple inheritance, you will need
        to create a module or subpackage for each module or subpackage
        that exists in more than one base package, and explicitly specify
        the right '__bases__' for it.  If a module or subpackage only
        appears in one base, however, and you have nothing to add to it,
        you can omit it from the inheriting package.


    Using Relative Imports in Packages

        If you want to extend a package, it's important to use only
        relative imports.  This is because the code of a module
        is executed as-is in the derived module.  If you do an
        absolute import, e.g. 'import foo.baz' in package 'foo.bar',
        then 'spam.bar' will still import 'foo.baz', not 'spam.baz'.
        It's better to 'import baz' for an item in the same package,
        or use 'peak.utils.imports.lazyModule' like this::

            from peak.utils.imports import lazyModule
            baz = lazyModule(__name__, 'baz')

        While this is more verbose in the simple case, it works for
        more complex relative paths than Python allows; for example
        you can do this::

            eggs = lazyModule(__name__, '../ni/eggs')

        which isn't possible with a regular 'import' statement.








    Import Paths

        To make using relative imports easier, '__bases__' can include
        "/"-separated relative path strings instead of modules, e.g.::

            __bases__ = '../../foo/bar',

        A / at the beginning of the path makes it absolute, so '/foo/bar'
        would also work.


    To-do Items

        * The simulator should issue warnings for a variety of questionable
          situations, such as...

          - Code matching the following pattern, which doesn't do what it looks
            like it does, and should probably be considered a "serious order
            disagreement"::

            BaseModule:

                class Foo: ...

                class Bar: ...

            DerivedModule:

                class Bar: ...

                class Foo(Bar): ...

        * This docstring is woefully inadequate to describe all the interesting
          subtleties of module inheritance; a tutorial is really needed.  But
          there *does* need to be a reference-style explanation as well, that
          describes the precise semantics of interpretation for assignments,
          'def', and 'class', in modules running under simulator control.




        * Allow 'declareModule()' to bootstrap non-existent modules; this might
          let us create "virtual packages" made by assembling other packages
          and modules.

        * Need a strategy for handling "del" operations; they are currently
          untrapped.  This might be okay under most circumstances, but need to
          consider edge cases.

        * 'makeClass()' should probably become part of the core API, where
          it can be used to resolve __metaclass__ conflicts during the first
          pass of importing a module (prior to running 'setupModule()')
"""





























from __future__ import generators
import sys
from types import ModuleType
from peak.util.EigenData import AlreadyRead
from peak.util._Code import codeIndex
from peak.util.imports import lazyModule, joinPath, getModuleHooks
from protocols.advice import isClassAdvisor

# Make the default value of '__proceed__' a built-in, so that code written for
# an inheriting module won't fail with a NameError if there's no base module
# definition of a function

import __builtin__; __builtin__.__proceed__ = None


__all__ = [
    'patchModule', 'setupModule', 'setupObject', 'ModuleInheritanceWarning',
    'declareModule', 'SpecificationError',
]

patchMap = {}


def setupObject(obj, **attrs):

    """Set attributes without overwriting values defined in a derived module"""

    for k,v in attrs.items():
        if not hasattr(obj,k):
            setattr(obj,k,v)











def toBases(bases,name=''):

    if isinstance(bases,(str,ModuleType)):
        bases = bases,

    for b in bases:

        if isinstance(b,str):
            b = lazyModule(name,b)

        yield b


def moduleBases(module, name=''):
    return tuple(toBases(getattr(module,'__bases__',()), name))


class SpecificationError(Exception):
    pass






















def getLegacyCode(module):

    # XXX this won't work with zipfiles yet

    from imp import PY_COMPILED, PY_SOURCE, get_magic, get_suffixes

    file = module.__file__

    for (ext,mode,typ) in get_suffixes():

        if file.endswith(ext):

            if typ==PY_COMPILED:

                f = open(file, mode)

                if f.read(4) == get_magic():
                    f.read(4)   # skip timestamp
                    import marshal
                    code = marshal.load(f)
                    f.close()
                    return code

                # Not magic!
                f.close()
                raise AssertionError("Bad magic for %s" % file)


            elif typ==PY_SOURCE:

                f = open(file, mode)
                code = f.read()
                f.close()

                if code and not code.endswith('\n'):
                    code += '\n'

                return compile(code, file, 'exec')

    raise AssertionError("Can't retrieve code for %s" % module)

def getCodeListForModule(module, code=None):

    if hasattr(module,'__codeList__'):
        return module.__codeList__

    if code is None:
        code = getLegacyCode(module)

    name = module.__name__
    code = prepForSimulation(code)
    codeList = module.__codeList__ = patchMap.get(name,[])+[code]

    bases = moduleBases(module, name)

    path = getattr(module,'__path__',[])

    for baseModule in bases:

        if not isinstance(baseModule,ModuleType):
            raise TypeError (
                "%s is not a module in %s __bases__" % (baseModule,name)
            )

        for p in getattr(baseModule,'__path__',()):
            if p in path: path.remove(p)
            path.append(p)

        for c in getCodeListForModule(baseModule):
            if c in codeList: codeList.remove(c)
            codeList.append(c)

    if path:
        module.__path__ = path

    return codeList






declarations = {}   # just keeps track

def declareModule(name, relativePath=None, bases=(), patches=()):

    """Package Inheritance Shortcut and Third-party Patches

    This function lets you "pre-declare" that a module should have
    some set of bases or "patch modules" applied to it.  This lets
    you work around the single-inheritance limitation of package
    inheritance, and it also lets you apply "patch modules" to
    third-party code that doesn't call 'setupModule()'.

    To use this, you must call it *before* the module has been
    imported, even lazily.  You can call it again as many times
    as you like, as long as the base and patch lists remain the
    same for a given module.  Also note that the module must *exist*;
    that is, there must be some Python-findable source or bytecode
    for the specified module.  It can be "inherited" via package
    inheritance from its containing package's base package; you just
    can't make up a phony module name and have it work.  (This limitation
    might get lifted later, if it turns out to be useful.)

    'bases' are placed in the target module's '__bases__', *after*
    any bases declared in the package.  'patches' are applied as
    though they were the first modules to call 'patchModule()'.
    So the overall "MRO" for the resulting module looks like this:

        1. patches by modules calling 'patchModule()'

        2. modules specified by 'declareModule(patches=)'

        3. the module itself

        4. any '__bases__' declared by the module

        5. base modules supplied by 'declareModule(bases=)'

    Note that both 'bases' and 'patches' may be modules,
    relative paths to modules (relative to the declared module,
    *not* the 'name' parameter), or tuples of modules or paths.

    Using 'declareModule()' makes it easier to do multiple inheritance
    with packages.  For example, suppose you have packages 'square'
    and 'circle', and want to make a package 'curvyBox' that inherits
    from both.

    Further suppose that the 'square' package contains a 'square.rect'
    module, and a 'square.fill' module, and 'circle' contains a
    'circle.curve' module, and a 'circle.fill' module.  Because of
    the way the Python package '__path__' attribute works, package
    inheritance won't combine the '.fill' modules; instead, it will
    pick the first '.fill' module found.

    To solve this, we could create a 'curvyBox.fill' module that inherited
    from both 'square.fill' and 'circle.fill'.  But if there are many such
    modules or subpackages, and they will be empty but for '__bases__', we
    can use 'declareModule()' to avoid having to create individual
    subdirectories and '.py' files.

    This can be as simple as creating 'curvyBox.py' (or
    'curvybox/__init__.py'), and writing this code::

        from peak.api import *

        __bases__ = '../square', '../circle'

        config.declareModule(__name__, 'fill',
            bases = ('../../circle/fill',)  # relative to 'curvyBox.fill'
        )

        config.setupModule()

    This will add 'circle.fill' to the '__bases__' of 'curvyBox.fill' (which
    will be the inherited 'square.fill' module.

    Another usage of 'declareModule()' is to patch a third-party module::

        import my_additions
        config.declareModule('third.party.module', patches=(my_additions,))
    """


    if relativePath:
        name = joinPath(name, relativePath)

    if name in declarations:

        if declarations[name]==(bases,patches):
            return lazyModule(name)  # already declared it this way

        raise SpecificationError(
            ("%s has already been declared differently" % name),
            patches, declarations[name]
        )

    declarations[name] = bases, patches


    def load(module):

        if hasattr(module,'__codeList__'):  # first load might leave code
            del module.__codeList__

        plist = patchMap.setdefault(name, [])
        for patch in toBases(patches, name):
            plist.extend(getCodeListForModule(patch))

        module.__bases__ = moduleBases(module,name) + tuple(toBases(bases,name))
        buildModule(module)


    # ensure that we are run before any other 'whenImported' hooks
    getModuleHooks(name).insert(0, load)

    return lazyModule(name)








def setupModule():

    """setupModule() - Build module, w/patches and inheritance

    'setupModule()' should be called only at the very end of a module's
    code.  This is because any code which follows 'setupModule()' will be
    executed twice.  (Actually, the code before 'setupModule()' gets
    executed twice, also, but the module dictionary is reset in between,
    so its execution is cleaner.)
    """

    frame = sys._getframe(1)
    dict = frame.f_globals

    if dict.has_key('__PEAK_Simulator__'):
        return

    code = frame.f_code
    name = dict['__name__']
    module = sys.modules[name]

    buildModule(module, code)



















def buildModule(module, code=None):

    codelist = getCodeListForModule(module, code)
    d = module.__dict__

    if len(codelist)>1:
        saved = {}
        for name in '__file__', '__path__', '__name__', '__codeList__':
            try:
                saved[name] = d[name]
            except KeyError:
                pass

        d.clear()
        d.update(saved)

        sim = Simulator(d)   # Must happen after!

        map(sim.execute, codelist)
        sim.finish()

    if '__init__' in d:
        d['__init__']()


















def patchModule(moduleName):

    """"Patch" a module - like a runtime (aka "monkey") patch, only better

        Usage::

            from peak.api import config

            # ... body of module

            config.patchModule('moduleToPatch')

    'patchModule()' works much like 'setupModule()'.  The main difference
    is that it applies the current module as a patch to the supplied module
    name.  The module to be patched must not have been imported yet, and it
    must call 'setupModule()'.  The result will be as though the patched
    module had been replaced with a derived module, using the standard module
    inheritance rules to derive the new module.

    Note that more than one patching module may patch a single target module,
    in which case the order of importing is significant.  Patch modules
    imported later take precedence over those imported earlier.  (The target
    module must always be imported last.)

    Patch modules may patch other patch modules, but there is little point
    to doing this, since both patch modules will still have to be explicitly
    imported before their mutual target for the patches to take effect.
    """

    frame = sys._getframe(1)
    dict = frame.f_globals

    if dict.has_key('__PEAK_Simulator__'):
        return

    if dict.has_key('__bases__'):
        raise SpecificationError(
            "Patch modules cannot use '__bases__'"
        )


    if sys.modules.has_key(moduleName):
        raise AlreadyRead(
            "%s is already imported and cannot be patched" % moduleName
        )

    code = frame.f_code
    name = dict['__name__']
    module = sys.modules[name]

    codelist = getCodeListForModule(module, code)
    patchMap.setdefault(moduleName, [])[0:0] = codelist



from peak.util.Code import *

from peak.util.Code import BUILD_CLASS, STORE_NAME, MAKE_CLOSURE, \
    MAKE_FUNCTION, LOAD_CONST, STORE_GLOBAL, CALL_FUNCTION, IMPORT_STAR, \
    IMPORT_NAME, JUMP_ABSOLUTE, POP_TOP, ROT_FOUR, LOAD_ATTR, LOAD_GLOBAL, \
    LOAD_CONST, ROT_TWO, LOAD_LOCALS, STORE_SLICE, DELETE_SLICE, STORE_ATTR, \
    STORE_SUBSCR, DELETE_SUBSCR, DELETE_ATTR, DELETE_NAME, DELETE_GLOBAL

from peak.util.Meta import makeClass
from warnings import warn, warn_explicit

class ModuleInheritanceWarning(UserWarning):
    pass

mutableOps = (
    STORE_SLICE,  STORE_SLICE+1,  STORE_SLICE+2,  STORE_SLICE+3,
    DELETE_SLICE, DELETE_SLICE+1, DELETE_SLICE+2, DELETE_SLICE+3,
    STORE_ATTR,   DELETE_ATTR,    STORE_SUBSCR,   DELETE_SUBSCR,
)








class Simulator:

    def __init__(self, dict):
        self.advisors  = {}
        self.defined   = {}
        self.locked    = {}
        self.funcs     = {}
        self.lastFunc  = {}
        self.classes   = {}
        self.classPath = {}
        self.setKind   = {}
        self.dict      = dict

    def execute(self, code):

        d = self.dict

        try:
            d['__PEAK_Simulator__'] = self
            exec code in d

        finally:
            del d['__PEAK_Simulator__']
            self.locked.update(self.defined)
            self.defined.clear()
            self.setKind.clear()
            self.classPath.clear()

    def finish(self):
        for k,v in self.lastFunc.items():
            bind_func(v,__proceed__=None)










    def ASSIGN_VAR(self, value, qname):

        locked = self.locked

        if locked.has_key(qname):

            if self.setKind.get(qname)==STORE_NAME:
                warn(
                    "Redefinition of variable locked by derived module",
                    ModuleInheritanceWarning, 2
                )

            return locked[qname]

        self.defined[qname] = value
        self.setKind[qname] = STORE_NAME
        return value
























    def DEFINE_FUNCTION(self, value, qname):

        if self.setKind.get(qname,IMPORT_STAR) != IMPORT_STAR:
            warn(
                ("Redefinition of %s" % qname),
                ModuleInheritanceWarning, 2
            )

        self.setKind[qname] = MAKE_FUNCTION

        lastFunc, locked, funcs = self.lastFunc, self.locked, self.funcs

        if lastFunc.has_key(qname):
            bind_func(lastFunc[qname],__proceed__=value); del lastFunc[qname]

        if '__proceed__' in value.func_code.co_names:
            lastFunc[qname] = value

        if locked.has_key(qname):
            return locked[qname]

        if funcs.has_key(qname):
            return funcs[qname]

        funcs[qname] = value
        return value















    def IMPORT_STAR(self, module, locals, prefix):

        locked = self.locked
        have = locked.has_key
        defined = self.defined
        setKind = self.setKind
        checkKind = setKind.get

        def warnIfOverwrite(qname):
            if checkKind(qname,IMPORT_STAR) != IMPORT_STAR:
                warn(
                    ("%s may be overwritten by 'import *'" % qname),
                    ModuleInheritanceWarning, 3
                )
            setKind[qname]=IMPORT_STAR

        all = getattr(module,'__all__',None)

        if all is None:

            for k,v in module.__dict__.items():
                if not k.startswith('_'):
                    qname = prefix+k
                    if not have(qname):
                        warnIfOverwrite(qname)
                        locals[k] = defined[qname] = v

        else:
            for k in all:
                qname = prefix+k
                warnIfOverwrite(qname)
                if not have(qname):
                    warnIfOverwrite(qname)
                    locals[k] = defined[qname] = getattr(module,k)







    def DEFINE_CLASS(self, name, bases, cdict, qname):

        if self.setKind.get(qname,IMPORT_STAR) != IMPORT_STAR:
            warn(
                ("Redefinition of %s" % qname),
                ModuleInheritanceWarning, 2
            )

        self.setKind[qname] = BUILD_CLASS

        mc = cdict.get('__metaclass__')

        if mc is not None:

            while isClassAdvisor(mc):
                cb = getattr(mc,'callback',None)
                if cb is not None:
                    self.advisors.setdefault(qname,[]).append(cb)
                mc = mc.previousMetaclass

            if mc is None:
                del cdict['__metaclass__']
            else:
                cdict['__metaclass__'] = mc


        classes = self.classes
        get = self.classPath.get
        oldDPaths = []
        basePaths = tuple([get(id(base)) for base in bases])
        dictPaths = [(k,get(id(v))) for (k,v) in cdict.items() if get(id(v))]










        if classes.has_key(qname):

            oldClass, oldBases, oldPaths, oldItems, oldDPaths = classes[qname]
            addBases = []; addBase = addBases.append
            addPaths = []; addPath = addPaths.append

            for b,p in zip(oldBases, oldPaths):
                if p is None or p not in basePaths:
                    addBase(classes.get(p,(b,))[0])
                    addPath(p)

            bases = tuple(addBases) + bases
            basePaths = tuple(addPaths) + basePaths

            have = cdict.has_key
            for k,v in oldItems:
                if not have(k): cdict[k]=v

            for k,v in oldDPaths:
                cdict[k] = classes[v][0]

        if '.' in qname:    # try to set __name__ if nested class
            cdict['__name__'] = qname

        newClass = makeClass(qname,bases,cdict)

        classes[qname] = newClass, bases, basePaths, cdict.items(), \
            dict(dictPaths+oldDPaths).items()

        # Make sure that module and name are correct for pickling

        newClass.__module__ = self.dict['__name__']
        self.classPath[id(newClass)] = qname

        # Apply callbacks
        if qname in self.advisors:
            cbs = self.advisors[qname][:]
            while cbs:
                newClass = cbs.pop()(newClass)


        locked = self.locked
        if locked.has_key(qname):
            return locked[qname]

        # Save the class where pickle can find it
        self.dict[qname] = newClass

        return newClass

































def prepForSimulation(code, path='', depth=0):

    code = Code(code)
    idx = codeIndex(code); opcode, operand = idx.opcode, idx.operand
    offset = idx.offset
    name_index = code.name_index
    const_index = code.const_index
    append = code.co_code.append

    Simulator = name_index('__PEAK_Simulator__')
    DefFunc   = name_index('DEFINE_FUNCTION')
    DefClass  = name_index('DEFINE_CLASS')
    Assign    = name_index('ASSIGN_VAR')
    ImpStar   = name_index('IMPORT_STAR')

    names   = code.co_names
    consts  = code.co_consts
    co_code = code.co_code

    emit = code.append
    patcher = iter(code); patch = patcher.write; go = patcher.go
    spc = '    ' * depth

    for op in mutableOps:
        for i in idx.opcodeLocations(op):
            warn_explicit(
                "Modification to mutable during initialization",
                ModuleInheritanceWarning,
                code.co_filename,
                idx.byteLine(offset(i)),
            )

    for op in (DELETE_NAME, DELETE_GLOBAL):
        for i in idx.opcodeLocations(op):
            warn_explicit(
                "Deletion of global during initialization",
                ModuleInheritanceWarning,
                code.co_filename,
                idx.byteLine(offset(i)),
            )

    ### Fix up IMPORT_STAR operations

    for i in idx.opcodeLocations(IMPORT_STAR):

        backpatch = offset(i)

        if opcode(i-1) != IMPORT_NAME:
            line = idx.byteLine(backpatch)
            raise AssertionError(
                "Unrecognized 'import *' at line %(line)d" % locals()
            )

        patchTarget = len(co_code)
        go(offset(i-1))
        patch(JUMP_ABSOLUTE, patchTarget, 0)

        # rewrite the IMPORT_NAME
        emit(IMPORT_NAME, operand(i-1))

        # Call __PEAK_Simulator__.IMPORT_STAR(module, locals, prefix)
        emit(LOAD_GLOBAL, Simulator)
        emit(LOAD_ATTR, ImpStar)
        append(ROT_TWO)
        append(LOAD_LOCALS)
        emit(LOAD_CONST, const_index(path))
        emit(CALL_FUNCTION, 3)
        emit(JUMP_ABSOLUTE, backpatch)

        # Replace IMPORT_STAR w/remove of the return val from IMPORT_STAR()
        co_code[offset(i)] = POP_TOP

        #print "%(line)04d import * (into %(path)s)" % locals()









    ### Fix up all other operation types

    for i in list(idx.opcodeLocations(STORE_NAME))+list(
        idx.opcodeLocations(STORE_GLOBAL)
    ):

        op     = opcode(i)
        arg    = operand(i)
        prevOp = opcode(i-1)
        qname = name = names[arg]

        backpatch = offset(i)
        patchTarget = len(co_code)

        if path and opcode(i)==STORE_NAME:
            qname = path+name

        namArg = const_index(qname)

        # common prefix - get the simulator object
        emit(LOAD_GLOBAL, Simulator)




















        ### Handle class operations

        if prevOp == BUILD_CLASS:

            bind = "class"

            if opcode(i-2)!=CALL_FUNCTION or \
               opcode(i-3) not in (MAKE_CLOSURE, MAKE_FUNCTION) or \
               opcode(i-4)!=LOAD_CONST:

                line = idx.byteLine(backpatch)
                raise AssertionError(
                    "Unrecognized class %(qname)s at line %(line)d" % locals()
                )

            const = operand(i-4)
            suite = consts[const]
            consts[const] = prepForSimulation(suite, qname+'.', depth+1)

            backpatch -= 1  # back up to the BUILD_CLASS instruction...
            nextI = offset(i+1)

            # and fill up the space to the next instruction with POP_TOP, so
            # that if you disassemble the code it looks reasonable...

            for j in range(backpatch,nextI):
                co_code[j] = POP_TOP

            # get the DEFINE_CLAS method
            emit(LOAD_ATTR, DefClass)

            # Move it before the (name,bases,dict) args
            append(ROT_FOUR)

            # Get the absolute name, and call method w/4 args
            emit(LOAD_CONST, namArg)
            emit(CALL_FUNCTION, 4)




        ### Non-class definition

        else:
            if prevOp in (MAKE_FUNCTION, MAKE_CLOSURE):
                bind = "def"
                # get the DEFINE_FUNCTION method
                emit(LOAD_ATTR, DefFunc)
            else:
                bind = "assign"
                # get the ASSIGN_VAR method
                emit(LOAD_ATTR, Assign)

            # Move it before the value, get the absolute name, and call method
            append(ROT_TWO)
            emit(LOAD_CONST, namArg)
            emit(CALL_FUNCTION, 2)



        # Common patch epilog

        go(backpatch)
        patch(JUMP_ABSOLUTE, patchTarget, 0)

        emit(op, arg)
        emit(JUMP_ABSOLUTE, offset(i+1))

        #print "%(line)04d %(spc)s%(bind)s %(qname)s" % locals()

    code.co_stacksize += 5  # add a little margin for error
    return code.code()


bind_func(prepForSimulation, **globals())
bind_func(prepForSimulation, **getattr(__builtins__,'__dict__',__builtins__))






if __name__=='__main__':
    from glob import glob
    for file in glob('ick.py'):
        print
        print "File: %s" % file,
        source = open(file,'r').read().rstrip()+'\n'
        try:
            code = compile(source,file,'exec')
        except SyntaxError:
            print "Syntax Error!"
        else:
            print
        code = prepForSimulation(code)
    print



























