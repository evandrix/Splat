"""MethodExporter"""

__all__ = [
    'MethodExporter'
]


from types import FunctionType
from new import instancemethod
from peak.binding.once import ActiveClass, getInheritedRegistries
from kjbuckets import kjGraph
import protocols





























class MethodExporter(protocols.ProviderMixin,ActiveClass):

    """Support for generating "verbSubject()" methods from template functions

        MethodExporter is a metaclass whose instances are singletons that
        install "verbSubject()"-style methods in classes which contain them.
        The verbs are implemented as method templates in the class statement
        which defines the MethodExporter, and the subject name comes from
        the name of the class being defined.  (Note: the target class must have
        a metaclass based on 'binding.Activator', either through explicit
        definition or via inheritance from e.g. 'binding.Component'.)

        Usage example::

            class slappableFeature(object):

                __metaclass__ = MethodExporter

                message = "Ow, that hurts!"

                newVerbs = [ ('slap', "slap%(initCap)s") ]

                def slap(feature, self, extra):
                    print "%s: %s (%s)" % (self.name, feature.message, extra)

            class Person(object):

                __metaclass__ = binding.Activator

                def __init__(self,name):
                    self.name = name

                class face(slappableFeature):
                    message = "Watch out for my glasses!"

                class back(slappableFeature):
                    pass

            joe = Person('Joe')


            # Prints: "Joe: Watch out for my glasses! (Thanks, I needed that!)"
            joe.slapFace("Thanks, I needed that!")

            # Prints: "Joe: Ow, that hurts!  (Am I great or what?)"
            joe.slapBack("Am I great or what?")

        While a bit silly, this demonstrates how the method template 'slap()'
        is used to generate 'slapFace()' and 'slapBack()' methods, how to
        define a 'newVerbs' list, and the calling conventions for verbs.

        Typically, you will define MethodExporters with multiple verbs, and
        you may also use template variants, which are chosen by metadata in
        subclasses.  For example, suppose we wanted 'slappableFeatures' to
        implement the 'slap' verb differently depending on skin thickness::

            class slappableFeature(object):

                __metaclass__ = MethodExporter

                thickness = 5

                newVerbs = [ ('slap', "slap%(initCap)s") ]

                def slap_thick(feature, self):
                    print "THUD!", feature.thickness

                slap_thick.installIf = (
                    lambda feature,func: feature.thickness > 10
                )

                slap_thick.verb = "slap"

                def slap_thin(feature, self):
                    print "SMACK!", feature.thickness

                slap_thin.installIf = (
                    lambda feature,func: feature.thickness <= 10
                )

                slap_thin.verb = "slap"

            class Person(object):

                __metaclass__ = binding.Activator


                class face(slappableFeature):
                    thickness = 5

                class back(slappableFeature):
                    thickness = 15

            joe = Person()

            # two ways to print "SMACK! 5"
            joe.slapFace()
            Person.face.slap(joe)

            # two ways to print "THUD! 15"
            joe.slapBack()
            Person.back.slap(joe)


        As you can see from this example, 'face' and 'back' actually do exist
        as real attributes of the 'Person' class.  They are instances of
        MethodExporter, class-like objects created by their respective class
        statements.  MethodExporter instances are singleton-like: any functions
        defined in a MethodExporter which are not templates (i.e., do not
        have a 'verb' and aren't listed in the 'newVerbs' list) will become
        methods of the MethodExporter itself, rather than methods of the
        containing class.  To distinguish such methods, and to keep clear the
        distinction between the feature and its container, we suggest using
        'feature' as the first parameter of such methods.  For example, we
        could rewrite the slap verb as::

            def yelp(feature):
                # This will be a method of the feature, because it is not
                # defined in 'newVerbs' of this class or a superclass
                print 'Y%sow!  My %s hurts!" % (
                    'e'*(20-feature.thickness), feature.attrName
                )

            def slap(feature, self):
                feature.yelp()

        This will print "Yeeeeeeeeeeeeeeeow!  My face hurts!" or
        "Yeeeeeow!  My back hurts!", as is appropriate for the specific
        feature.  We could also simply call 'Person.back.yelp()' or
        'Person.face.yelp()' to obtain the same results.

        By now, the sharp-eyed reader will be wondering about the bits of
        magic code that keep showing up, such as the '(feature, self)'
        parameter pattern, and the 'newVerbs' list.  Not to mention our earlier
        usage of the 'installIf' and 'verb' attributes.  So let's move on to
        the reference sections...

        Specifying Verbs with the 'newVerbs' class attribute

            The 'newVerbs' class attribute is a list of '(key,value)' tuples
            listing verbs introduced in the MethodExporter being defined.
            The keys are verb (inner method) names, and the values are format
            strings that are used to generate the outer method names.

            The format strings are applied to a 'nameMapping' object supplied
            by MethodExporter's 'subjectNames()' method.  The format strings
            are normal Python '%' formatting strings as applied to a mapping.
            The names in parentheses, such as '"initCap"' in
            '"slap%(initCap)s"', are looked up in the mapping object.

            'initCap' is the most commonly used name in a format string: it
            supplies the MethodExporter instance's name, with the first
            character capitalized.  But there are many other options.  For
            example, any attribute of the MethodExporter being defined can
            be used, like this::

                class Collection(someFeature):
                    single = 'item'
                    newVerbs = Items(add='add%(single)s')

            The above example will generate an 'additem()' method, unless a
            subclass changes the 'single' attribute to a different string.
            This lets you have subclasses change the name of what kind of
            objects are in a collection, and have the exported method names
            change accordingly.  (Notice also that you can use the peak.api
            'Items()' function to create a 'newVerbs' list; you don't have to
            do it by hand.)

            You can also use more complex formatting, using dotted names::

                class Collection(someFeature):
                    single = 'item'
                    newVerbs = Items(add='add%(single.initCap)s')

            This will apply the 'nameMapping.initCap()' method to the 'single'
            attribute before formatting, resulting in an 'addItem()' method.
            See the 'nameMapping' documentation for more details on how names
            used in format strings are interpreted.

        The 'installIf' function attribute

            The 'installIf' function attribute, if supplied, is a callable that
            takes two arguments: the feature (i.e. the MethodExporter instance
            which is being created), and the function.  If the callable returns
            a true value, the function will be used as the template for the
            appropriate verb (inner and outer forms).  If the callable returns
            false, the function will not be used.  Note that 'installIf'
            conditions should be arranged such that at most *one* can be true
            at a time, because if more than one is true, a 'TypeError' will be
            raised at class creation time.  If none of the 'installIf'
            conditions are true, the verb will not appear as a method of the
            feature class, nor will it be exported to any containing class.

        The 'verb' function attribute

            The normal use of 'installIf' is to select variant implementations
            of the same verb, based on metadata supplied in a subclass.  However,
            since the variants must have different function names, the 'verb'
            function attribute is used to indicate the name which will be used
            in the finished MethodExporter.  Thus, in our "thick and thin" slap
            example, using 'slap_thick.verb="slap"' and 'slap_thin.verb="slap"'
            caused either 'slap_thick' or 'slap_thin' to be installed as the
            'slap' method of the MethodExporter.  If you do not supply a
            'verb' function attribute, the function's name within the class
            is used.  Note that this does not have to be the function name;
            for example, the below defines a 'baz' verb, not 'foo'::

                def foo(self): pass

                class bar(object):
                    __metaclass__ = MethodExporter
                    newVerbs = Items(baz='baz%(initCap)s')
                    baz = foo

            Also note that methods are only exported if their 'verb' is listed
            in the 'newVerbs' of the class or one of its base classes.  You can
            make use of this behavior to create "private" verbs that are only
            accessible from the feature.  Just set the 'verb' attribute of
            your function templates to the name of the desired "private"
            method.

        Parameters and Calling Conventions

            All methods of a MethodExporter are defined as Python 'classmethod'
            objects.  (This is done for you automatically by MethodExporter, so
            you don't have to explicitly declare them as such.)

            Being class methods, the first parameter of any method or method
            template that you place in a MethodExporter class is always the
            class.  By convention in PEAK, this parameter is named
            'feature', but you may use any name that makes sense to you.  When
            the method executes, this parameter will refer to the
            MethodExporter, so you can access its attributes and methods.  For
            simple methods of the MethodExporter itself, this is the only
            parameter which you *must* define.

            Method templates, however, must take a second parameter, named
            'self' by convention in PEAK.  This parameter will receive
            the instance of the containing class that the MethodExporter is
            being used in.  Any further parameters beyond this point belong
            to the signature of your method template and are not defined or
            used by the infrastructure.

            This approach allows method templates to do double duty.  They
            can be used as class methods and passed an instance of the outer
            class, or they can be used directly as instance methods of the
            outer class.

        Dynamic Method Templates

            By using the 'isTemplate' function attribute, you can indicate that
            the function should be called in order to obtain the actual code to
            be used.  Here's the earlier code generation example, rewritten
            using dynamic templates::

                class slappableFeature(object):

                    __metaclass__ = MethodExporter

                    thickness = 5

                    newVerbs = [ ('slap', "slap%(initCap)s") ]

                    def slap(feature):

                        if feature.thickness > 10:

                            def slap(feature, self):
                                print "THUD!", feature.thickness

                        else:
                            def slap(feature, self):
                                print "SMACK!", feature.thickness

                        return slap

                    slap.isTemplate = True


            As you can see, this can often be a more readable approach, if you
            don't need to redefine the variants in subclasses.  The outer
            'slap' function shown above is passed the feature object (or one
            of its subclasses) being defined, and must return the function to
            be used as a verb implementation.  If it returns 'None', the verb
            will not exist in the defined feature, nor will it be exported to
            any class the feature is placed in.

            The same rules apply for recognizing a template as any other verb
            implementation: it must be named the same as a verb, or it must
            have a 'verb' function attribute identifying the appropriate verb.
            It can also have an 'installIf' attribute, if desired.  The
            'installIf' attribute is checked first, and the template function
            is only called if the 'installIf' check returns a true value.

        Inner and Outer Method Definitions

            Sometimes, one needs to modify an "off-the-shelf" method
            exported by a MethodExporter.  For this reason, MethodExporters
            do not overwrite methods which are already defined in their
            containing class.  For example, if we defined Person as follows::

                class Person(object):

                    class face(slappableFeature):
                        thickness = 5

                    class back(slappableFeature):
                        thickness = 15

                    def slapBack(self):
                        self.__class__.back.slap(self)
                        print "Do you really have to do that?"

                    def slapFace(self):
                        print "Don't even think about it!"

            Then 'aPerson.slapFace()' would print "Don't even think about it",
            while 'aPerson.slapBack()' would carry out the generated behavior,
            and then ask, "Do you really have to do that?".  Subclasses of
            Person will retain these modified behaviors, even if 'back' is
            redefined in the subclass.  (In which case, the redefined behavior
            will be followed by the "Do you really have to do that?" question.)

        Overriding Templates in Subclasses

            If you override a template in a subclass, you don't need to specify
            its 'verb', since that method name is already associated with the
            verb.  However, if you need an 'installIf' condition you must
            specify it in the subclass as well; otherwise it will be treated
            as an unconditional template, which may lead to conflict between
            install conditions.

            Note that the above rules apply to any template you override,
            regardless of its name, as long as it existed in the superclass.
            If you add a new template for an existing or new verb, you *must*
            specify its 'verb' attribute, or it must be an exported verb
            defined in the subclass' 'newVerbs' list.

        Why 'self.__class__.back'?

            Sharp-eyed Pythonistas may wonder why we don't just say
            'self.back' and be done with it.  The reason is that features
            can also be properties, so 'self.back' might actually be the
            instance value of the property defined by the feature.
            'self.__class__.back' will always be the class' definition of the
            feature 'back', which is what we want.

            The SEF framework adds '__get__', '__set__', and '__delete__'
            methods to a subclass of MethodExporter, which lets you create
            features that are properties; look at the
            'peak.model.api.FeatureClass' class for more details.

        Implementation Notes

            It's amazing that it takes so much documentation to describe so
            little code.  The combined docstrings for this metaclass are over
            *three times the size of the actual code*.  So if you've already
            read this far, you might as well read the source if you have a need
            to understand the actual implementation.  :)"""


    def subjectNames(self):
        """Return a nameMapping object for this feature"""
        return nameMapping(self)





    def getMethod(self, ob, verb):

        """Look up a method dynamically

        Sometimes, one wishes to access a possibly-overridden method of a
        feature, knowing the verb and subject, but not the method name.
        That is, one knows about 'slap', and 'face', but not 'slapFace'.
        In that case, 'face.getMethod(object,"slap")' can be used to obtain
        the 'object.slapFace' method, without needing to know the naming
        convetions used by the object.

        Note that this is different than simply accessing 'face.slap',
        because the containing class might have defined its own
        'slapFace()' method.  That method would refer to 'face.slap'
        in order to call the original, un-overridden method generated
        by the 'face' feature."""

        return getattr(ob,self.methodNames[verb])

    def activateInClass(self,klass,attrName):

        """Install the feature's "verbSubject()" methods upon use in a class"""

        self = super(MethodExporter,self).activateInClass(klass,attrName)

        if attrName != self.attrName:
            raise TypeError(
                "Feature %s installed in %s as %s; must be named %s" %
                (self.attrName, klass, attrName, self.attrName)
            )

        for verb,methodName in self.methodNames.items():

            old = getattr(klass, methodName, None)

            # Safe to export if no method there, or if it is an exported verb
            if old is None or hasattr(old,'verb'):
                setattr(klass, methodName, MethodWrapper(getattr(self,verb)))

        return self

    def __init__(self, className, bases, classDict):

        """Set up method templates, name mapping, etc."""

        self.attrName = className.split('.')[-1]
        super(MethodExporter,self).__init__(className, bases, classDict)

        verbs = self.verbs = {}
        mt    = self.methodTemplates = {}
        vt    = kjGraph()

        for v in getInheritedRegistries(self,'verbs'):
            verbs.update(v)

        for d in getInheritedRegistries(self,'methodTemplates'):
            mt.update(d)

        for d in getInheritedRegistries(self,'verbTemplates'):
            vt += d

        self.verbTemplates = vt
        verbs.update(dict(classDict.get('newVerbs',[])))


        for methodName, func in classDict.items():

            if not isinstance(func,FunctionType):
                continue

            setattr(self,methodName,classmethod(func))
            mt[methodName]=func

            if hasattr(func,'verb'):
                vt[func.verb]=func.verb     # ensure verb itself is considered
                vt[func.verb]=methodName

            elif methodName in verbs:
                vt[methodName]=methodName



        names = self.subjectNames()
        mn = self.methodNames = {}

        for verb in vt.keys():

            candidates = []

            for implName in vt.neighbors(verb):
                try:
                    func = mt[implName]
                except KeyError:
                    continue

                installIf  = getattr(func,'installIf',None)

                if installIf is None or installIf(self,func):
                    candidates.append(func)

            if candidates:

                if len(candidates)>1:
                    raise TypeError(
                        ("More than one version of '%s' template applies"
                        % verb), self, candidates
                    )

                func, = candidates
                if getattr(func,'isTemplate',False):
                    func = func(self)
                    if not func:
                        setattr(self,verb,nullProperty(verb))
                        continue

                if verb in verbs:
                    mn[verb] = verbs[verb] % names

                setattr(self,verb,classmethod(func))

            else:
                setattr(self,verb,nullProperty(verb))

class nameMapping(object):

    """A mapping used for formatting outer method names

        This class implements a mapping object with a few special
        tricks.  Names to be looked up are split on '.', and then
        each name part is looked up first as a method of the
        nameMapping object itself.  If a method is found, it's called
        on the result of the previous lookup, or the default name
        if there was no previous lookup.  If a method isn't found,
        the name part is looked up in the dictionary of the
        MethodExporter the nameMapping was created for.

        See the documentation for individual method names to see what
        special names are available."""

    def __init__(self, exporter): self.exp = exporter

    def name(self, name=None):
        """name - returns the feature name"""
        return self.exp.attrName

    def upper(self, name):
        """upper - equivalent to previousName.upper()"""
        return name.upper()

    def lower(self, name):
        """lower - equivalent to previousName.lower()"""
        return name.lower()

    def capitalize(self, name):
        """capitalize - equivalent to previousName.capitalize()"""
        return name.capitalize()

    def initCap(self, name):
        """initCap - previous name with first character capitalized"""
        return name[:1].upper()+name[1:]




    def __getitem__(self,key):

        name = self.name()
        part = None
        getName = lambda n: getattr(self.exp,part)

        for part in key.split('.'):
            name = getattr(self,part,getName)(name)

        return name


class MethodWrapper(object):

    """MethodWrapper(function) -- create an instance-method descriptor"""

    def __init__(self, im_func):
        self.im_func = im_func

    def __get__(self, ob, typ=None):
        if typ is None: typ = ob.__class__
        return instancemethod(self.im_func, ob, typ)


class nullProperty(object):

    __slots__ = 'attrName'

    def __init__(self,attrName):
        self.attrName = attrName

    def __get__(self, ob, typ=None):
        raise AttributeError, self.attrName

    __set__ = __delete__ = __get__






