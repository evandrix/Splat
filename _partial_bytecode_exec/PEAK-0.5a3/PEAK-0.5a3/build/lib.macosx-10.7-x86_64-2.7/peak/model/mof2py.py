"""Python code generation from MOF model

    This is still a little rough and the code it generates has not yet been
    tested.  In order to do that, we need to have a mechanism for indexing
    the created model, such that it can be used as a metamodel for
    'peak.storage.xmi'.

    Open issues:

    - There are a few unsupported features which will cause generated code
      not to work or not match the semantics of the supplied model:

        * We don't support actual "pure structure" types; specifically we
          don't generate correct code for the structure fields.

        * Package inheritance is not supported

        * Constants, TypeAliases, Constraints, Operations, Exceptions,
          Parameters, Associations, AssociationEnds and Tags do not have any
          code generated for them.

        * If a model name conflicts with Python keywords, built-ins, or a
          private/system ('_'-prefixed) name, the generated model may fail
          with no warning from the generator.

    - Docstring formatting is a bit "off"; notably, we're not wrapping
      paragraphs, and something seems wrong with linespacing, at least
      in my tests with the CWM metamodel.  This may be purely specific
      to CWM.  At least 'happydoc' seems to make some sense out of the
      docstrings it sees (non-nested classes only, alas).
"""










from __future__ import generators

from peak.api import *
from peak.util.IndentedStream import IndentedStream
from cStringIO import StringIO
from peak.util.advice import advice

from os.path import dirname,exists
from os import makedirs


class oncePerObject(advice):

    def __call__(self,*__args,**__kw):

        if __args[1] in __args[0].objectsWritten:
            return

        __args[0].objectsWritten[__args[1]]=True

        return self._func(*__args,**__kw)




















class MOFGenerator(binding.Component):

    metamodel = binding.Obtain("import:peak.metamodels.MOF131:")
    Package   = \
    Import    = \
    Class     = \
    Tag       = \
    DataType  = \
    Attribute = \
    Reference = \
    Namespace = \
    NameNotFound = \
    NameNotResolved = \
    StructuralFeature = binding.Delegate("metamodel")

    Composite = binding.Obtain("metamodel/AggregationKind/composite")

    fileObject = binding.Make(StringIO)

    stream = binding.Make(lambda self: IndentedStream(self.fileObject))
    write  = binding.Obtain('stream/write')
    push   = binding.Obtain('stream/push')
    pop    = binding.Obtain('stream/pop')

    objectsWritten = binding.Make(dict)

    pkgPrefix  = ''
    srcDir     = ''
    writeFiles = False

    sepLine = '# ' + '-'*78 + '\n'

    enumerationUnprefix = binding.Make(dict)








    def writeDocString(self, doc):

        doc = doc.replace('\\','\\\\')          # \   -> \\

        tq = 0
        while doc.endswith('"'):
            tq += 1
            doc=doc[:-1]

        if tq:
            # Replace trailing quotes with escaped quotes
            doc += '\\"' * tq

        doc = doc.replace('"""','\\"\"\\"')     # """ -> \"\"\"

        self.write('\n"""%s"""\n\n' % doc.encode('latin1'))


    def writeClassHeader(self, element, baseNames=[]):

        if baseNames:
            bases = '(%s)' % (', '.join(baseNames))
        else:
            bases = ''

        self.write('\nclass %s%s:\n' % (element.name,bases))
        self.push(1)

        if element.annotation:
            self.writeDocString(element.annotation)











    def beginObject(self, element, metatype='_model.Element'):

        ns = element.container
        relName = self.getRelativeName

        if hasattr(element,'supertypes'):

            baseNames = [relName(m,ns) for m in element.supertypes]

            if not baseNames:
                baseNames.append(metatype)

        else:
            baseNames = [metatype]

        self.writeClassHeader(element, baseNames)


    def getImportName(self, element):
        return self.pkgPrefix + str('.'.join(element.qualifiedName))


    def acquire(self, element, name):

        for p in self.iterParents(element):
            if not isinstance(p,self.Namespace): continue
            try:
                return p.lookupElement(name)
            except self.NameNotFound:
                pass



    def iterParents(self, element):

        while element is not None:
            yield element
            element = element.container



    def comparePaths(self, e1, e2):

        p1 = list(self.iterParents(e1)); p1.reverse()
        p2 = list(self.iterParents(e2)); p2.reverse()

        common = [i1 for (i1,i2) in zip(p1,p2) if i1 is i2]

        cc = len(common)
        p1 = p1[cc:]
        p2 = p2[cc:]

        return common, p1, p2


    def getImportPath(self, package, element):

        try:
            path = self.getRelativePath(package,element,False)

        except self.NameNotResolved:

            path = ['..']*len(package.qualifiedName) + element.qualifiedName

            if package.name == '__init__':
                # remove one level of '..'
                path = path[1:]

        return str('/'.join(path))













    def getRelativePath(self, e1, e2, acquire=True):

        c,p1,p2 = self.comparePaths(e1,e2)

        if c:
            if not p2:
                p1.insert(0,c[-1])
                p2.insert(0,c[-1])
                c.pop()

            if acquire:
                ob = self.acquire(e1,p2[0].name)

                if ob is p2[0]:
                    p1=[]   # just acquire it

            return ['..']*len(p1)+[e.name for e in p2]

        p1.reverse()    # Search all parents of the source

        if not acquire:
            p1=[]

        for parent in p1:

            if not isinstance(parent,self.Package):
                continue

            for imp in parent.findElementsByType(self.Import):
                c,sp1,sp2 = self.comparePaths(imp.importedNamespace, e2)
                if c:
                    # sp2 is path from imp -> e2
                    return self.getRelativePath(e1,imp)+[e.name for e in sp2]

        raise self.NameNotResolved(
            "No path between objects", e1.qualifiedName, e2.qualifiedName
        )




    pkgImportMap = binding.Make(dict)

    def nameInPackage(self, element, package):

        pim = self.pkgImportMap

        try:
            return pim[package, element]
        except KeyError:
            pass

        name = element.name
        c = element.container

        while c is not None and c is not package:
            try:
                ob = package.lookupElementExtended(name)
            except self.NameNotFound:
                break
            else:
                if ob is element:
                    break
                else:
                    name = '%s__%s' % (c.name, name)
                    c = c.container

        if element.container is not package:
            self.write(
                '%-20s = _lazy(__name__, %r)\n' % (
                    str(element.name),
                    self.getImportPath(package,element)
                )
            )

        pim[package,element] = name
        return name





    def writeFileHeader(self, package):
        self.write(self.sepLine)
        self.write('# Package: %s\n' % self.getImportName(package))
        self.write('# File:    %s\n' % self.pkgFileName(package))
        if package.supertypes:
            self.write('# Bases:   %s\n'
                % ', '.join(
                    [str('.'.join(p.qualifiedName))
                        for p in package.supertypes]
                )
            )
        if package.annotation:
            self.write(self.sepLine)
            self.writeDocString(package.annotation)
        self.write(self.sepLine)
        self.write("""
from peak.util.imports import lazyModule as _lazy

_model               = _lazy('peak.model.api')
#_config             = _lazy('peak.config.api')

""")


    def writeFileFooter(self, package):
        self.write(self.sepLine)
        self.write('\n#_config.setupModule()\n\n\n')

    def exposeImportDeps(self, package, target=None):

        if target is None: target = package
        nip = self.nameInPackage
        eid = self.exposeImportDeps

        for klass in target.findElementsByType(self.Class):
            for k in klass.supertypes:
                if k.container is not package:
                    nip(k.container, package)
            eid(klass)


    def writePackage(self, package):

        for subPkg in package.findElementsByType(self.Package):
            self.objectsWritten[subPkg] = True

        self.writeFileHeader(package)

        for imp in package.findElementsByType(self.Import):
            self.writeImport(imp)

        self.exposeImportDeps(package)

        for subPkg in package.findElementsByType(self.Package):
            self.write('%-20s = _lazy(__name__, %r)\n'
                % (subPkg.name, str(subPkg.name))
            )

        self.write('\n%s\n' % self.sepLine)
        self.writeNSContents(package,{})
        self.writeFileFooter(package)


    writePackage = oncePerObject(writePackage)


    def pkgFileName(self,package):

        from os.path import join
        path = self.srcDir

        for p in self.getImportName(package).split('.'):
            path = join(path,p)

        for ob in package.findElementsByType(self.Package):
            return join(path,'__init__.py')
        else:
            return '%s.py' % path




    def writeNSContents(self, ns, contentMap):

        for tag in self.findAndUpdate(ns, self.Tag, contentMap):
            if tag.tagId=='org.omg.xmi.enumerationUnprefix':
                for v in tag.values:
                    for e in tag.elements:
                        self.enumerationUnprefix[e] = v

        for imp in self.findAndUpdate(ns, self.Import, contentMap):
            self.writeImport(imp)

        for pkg in self.findAndUpdate(ns, self.Package, contentMap):
            self.writePackage(pkg)

        for klass in self.findAndUpdate(ns, self.Class, contentMap):
            self.writeClass(klass)

        for dtype in self.findAndUpdate(ns, self.DataType, contentMap):
            self.writeDataType(dtype)

        posn = 0
        for feature in self.findAndUpdate(
                ns, self.StructuralFeature, contentMap
            ):
            self.writeFeature(feature,posn)
            posn += 1

        # XXX constant, type alias, ...?


    def findAndUpdate(self, ns, findType, contentMap):

        for ob in ns.findElementsByType(findType):
            if ob.name in contentMap: continue
            contentMap[ob.name] = ob
            yield ob





    def writeImport(self, imp):

        pkgName = self.getImportPath(imp.container, imp.importedNamespace)
        self.write('%-20s = _lazy(__name__, %r)\n' % (imp.name, pkgName))

    writeImport = oncePerObject(writeImport)



    def writeClass(self, klass):

        myPkg = klass.container

        for c in klass.supertypes:
            if c.container is myPkg:
                self.writeClass(c)

        self.beginObject(klass, '_model.Element')

        if klass.isAbstract:

            if not klass.annotation:
                self.write('\n')

            self.write('mdl_isAbstract = True\n')

        contentMap = {}
        self.writeNSContents(klass, contentMap)

        if not contentMap and not klass.isAbstract:
            self.write('pass\n\n')
        else:
            self.write('\n')

        self.pop()

    writeClass = oncePerObject(writeClass)




    def writeDataType(self,dtype):

        tc = dtype.typeCode.unaliased()

        if tc.kind == model.TCKind.tk_enum:
            self.writeEnum(dtype, tc.member_names)

        elif tc.kind == model.TCKind.tk_struct:
            self.writeStruct(dtype, zip(tc.member_names,tc.member_types))

        else:

            base = model.basicTypes.get(tc.kind)

            if base is None:
                self.beginObject(dtype,'_model.PrimitiveType')
                self.write("pass   # XXX Don't know how to handle %s!!!\n\n"
                    % tc.kind
                )

            else:

                self.beginObject(dtype,'_model.'+base.__name__)

                if hasattr(tc,'length'):
                    self.write('length = %d\n\n' % tc.length)

                elif hasattr(tc,'fixed_digits'):
                    self.write('fixed_digits = %d\n' % tc.fixed_digits)
                    self.write('fixed_scale  = %d\n\n' % tc.fixed_scale)
                else:
                    self.write('pass\n\n')

            self.pop()

    writeDataType = oncePerObject(writeDataType)





    def writeStruct(self,dtype,memberInfo):

        self.beginObject(dtype,'_model.StructType')

        posn = 0
        for mname, mtype in memberInfo:
            self.writeStructMember(mname, mtype, posn)
            posn += 1

        self.push(1)
        self.pop()


    def writeStructMember(self,mname,mtype,posn):

        self.write('class %s(_model.structField):\n\n' % mname)
        self.push(1)

        self.write('referencedType = %r # XXX \n' % repr(mtype))
        self.write('sortPosn = %r\n\n' % posn)

        self.pop()


    def writeEnum(self,dtype,members):

        self.beginObject(dtype,'_model.Enumeration')
        prefix = self.enumerationUnprefix.get(dtype,'')

        for m in members:
            if prefix and m.startswith(prefix):
                self.write('%s = _model.enum(%r)\n'%(m, str(m[len(prefix):])))
            else:
                self.write('%s = _model.enum()\n' % m)

        if members:
            self.write('\n')

        self.pop()


    def getRelativeName(self, element, package):

        if element.container is package:
            return element.name

        return '%s.%s' % (
            self.nameInPackage(element.container,package),
            element.name
        )
































    def writeFeature(self,feature,posn):

        self.beginObject(feature,'_model.StructuralFeature')

        if not feature.isChangeable:
            self.write('isChangeable = False\n')

        self.write('referencedType = %r\n'
            % str('/'.join(self.getRelativePath(feature,feature.type)))
        )

        if isinstance(feature,self.Reference):

            inverseRef = self.findInverse(feature)

            if inverseRef is not None:
                self.write('referencedEnd = %r\n' % str(inverseRef.name))

            if feature.referencedEnd.otherEnd().aggregation == self.Composite:
                self.write('isComposite = True\n')

        elif feature.isDerived:
            self.write('isDerived = True\n')


        m = feature.multiplicity

        if m.upper <> model.UnlimitedInteger.UNBOUNDED:
            self.write('upperBound = %r\n' % m.upper)

        if m.lower <> 0:
            self.write('lowerBound = %r\n' % m.lower)

        self.write('sortPosn = %r\n' % posn)
        self.pop()






    def findInverse(self, feature):

        ae = feature.referencedEnd.otherEnd()

        for ref in feature.type.findElementsByTypeExtended(self.Reference):
            if ref.referencedEnd is ae:
                return ref



    def externalize(klass, metamodel, package, format, **options):

        s = StringIO()

        klass(
            package,
            metamodel=metamodel,
            stream=IndentedStream(s),
            **options
        ).writePackage(package)

        return s.getvalue()


    externalize = classmethod(externalize)
















class MOFFileSet(MOFGenerator):

    def externalize(klass, metamodel, package, format, **options):

        def doExt(package, parent):

            g = klass(
                package, metamodel=metamodel, **options
            )

            filename = g.pkgFileName(package)

            if g.writeFiles:

                d = dirname(filename)
                if not exists(d):
                    makedirs(d)

                g.fileObject = open(filename,'w')
                g.writePackage(package)
                contents = None

            else:
                g.writePackage(package)
                contents = g.fileObject.getvalue()

            outfiles = [ (filename, contents) ]

            for pkg in package.findElementsByType(metamodel.Package):
                outfiles.extend(doExt(pkg, g))


            return outfiles

        return doExt(package,package)


    externalize = classmethod(externalize)



class MOFOutline(MOFGenerator):

    def writePackage(self, package):

        self.write('package %s:\n' % package.name)
        self.push(1)
        self.write('# %s\n' % self.pkgFileName(package))
        self.writeNSContents(package, {})
        self.pop()


    def writeImport(self, imp):
        self.write(
            'import %s'
                % self.getImportName(imp.importedNamespace)
        )
        if imp.name!=imp.importedNamespace.name:
            self.write(' as %s' % imp.name)

        self.write('\n')


    def writeClass(self, klass):
        baseNames = [
            self.getRelativeName(c,klass.container) for c in klass.supertypes
        ]
        self.write(
            'class %s(%s):\n'
                % (klass.name, ','.join(baseNames))
        )
        self.push(1)
        self.writeNSContents(klass, {})
        self.pop()

    def writeDataType(self,dtype):
        pass

    def writeFeature(self,feature,posn):
        pass


def genPkg(modelDescr, modelFile, pkgBase, srcDir, progress=lambda *x:None):

    """Generate a 'peak.model' package from a MOF XMI file

    'modelDescr' -- title of the model, e.g. '"UML 1.3"'

    'modelFile' -- the XMI file to generate from

    'pkgBase' -- dotted package prefix, e.g. '"peak.metamodels.UML13.model."'

    'srcDir' -- directory prefix before 'pkgBase', e.g. '"./src"'

    'progress' -- a function that will be called with data about each
         MOF package written; useful for progress indicators.

    Any missing directories will be created, but '__init__.py' files will
    not be created for parent packages of the specified package, so the
    output will not be a valid package unless you add them yourself.  Files
    in the destination directory may be overwritten, but existing files that
    don't correspond to the MOF model contents will not be deleted.  If you
    regenerate a changed model, you might want to delete the target directory
    tree first.
    """

    roots = storage.xmi.fromFile(modelFile, config.makeRoot())

    from peak.metamodels import MOF131

    init = MOF131.Package(roots[0].getParentComponent(),
        name='__init__',
        annotation='Structural Model for %s - Generated from %s' % (modelDescr,modelFile),
        contents=[MOF131.Import(name=r.name, importedNamespace=r) for r in roots]
    )

    for r in roots+[init]:
        progress(
            r.externalize('fileset',
                writeFiles=True,pkgPrefix=pkgBase,srcDir=srcDir
            )
        )

def main(prefix=''):

    def progress(x): print x

    genPkg(
        'UML 1.3',
        prefix+'peak/metamodels/UML_1.3_01-12-02.xml',
        'peak.metamodels.UML13.model.', prefix, progress
    )

    genPkg(
        'UML 1.4',
        prefix+'peak/metamodels/UML_1.4_01-02-15.xml',
        'peak.metamodels.UML14.model.', prefix, progress
    )

    genPkg(
        'UML 1.5',
        prefix+'peak/metamodels/UML_1.5_02-09-03.xml',
        'peak.metamodels.UML15.model.', prefix, progress
    )

    genPkg(
        'CWM 1.0',
        prefix+'peak/metamodels/CWM_1.0_01-02-03.xml',
        'peak.metamodels.CWM10.model.', prefix, progress
    )

    genPkg(
        'CWM 1.1',
        prefix+'peak/metamodels/CWM_1.1_02-05-01.xml',
        'peak.metamodels.CWM11.model.', prefix, progress
    )

if __name__=='__main__':
    main()





