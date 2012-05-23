"""Base classes for storing/retrieving model objects via XMI format

    Because the XMI 1.x specs are incredibly confusing and self-contradictory,
    it's necessary for us to clarify our interpretations of the specs and
    what restrictions we are placing upon our implementation goals.

    Our intended uses of XMI are as follows:

     1. Processing of UML models saved by commonly-available design tools

     2. Code generation from MOF metamodels for modelling languages such as
        UML and CWM, which are supplied in XMI format by the OMG and other
        standards bodies.

     3. Use as a metadata-driven persistence and import/export format for
        PEAK applications.  (The idea being that a readable format that
        doesn't require custom coding would make it easy to experiment
        with domain model designs, and to create test suites and test
        data for domain logic verification before the "final" storage
        machinery is built.)

    Usage 1 only requires reading of XMI 1.0 and 1.1 features needed by
    UML models, and is effectively complete now.  Usage 2 requires support
    for reading 'XMI.any' and CORBA typecodes.  Usage 3 requires that we
    be able to write XMI files - and any version would suffice.  However,
    if we support both 1.0 and 1.1 format for writing XMI, then we could
    support doing automated transforms of UML content, generation of UML
    or other constructs from code or database schemas, etc.  So ideally,
    we should be able to write both 1.0 and 1.1.

    XMI 2.0 looks very promising from the perspective of future tool
    support, but unfortunately it will not help us with any usage but #3.
    It may also need a somewhat differently structured implementation.  So
    for now we will mostly ignore XMI 2.0.  However, 2.0 introduces the idea
    of using tagged values on a metamodel to specify implementation
    details such as variations in tag or attribute names, etc., that would
    be useful to have for our intended applications.  So, where applicable,
    we will represent these tagged values as PEAK configuration properties
    of the form 'org.omg.xmi.*' corresponding to the official XMI tag
    names for those configuration options.

    Within the XMI 1.x series, we will not support the 'XMI.TypeDefinitions'
    block and its contents.  Survey of existing XMI files suggests this is
    not used in practice, and it was removed as of the XMI 1.2 spec.
    Unfortunately, we *do* have to support the 'XMI.Corba*' tags, as they
    are used by metamodels (such as UML and CWM) that are defined based on
    MOF 1.3 or earlier.  (MOF 1.4 and up abandon Corba typecodes as a basis
    for metamodel definition; unfortunately, few systems of interest to us
    are presently based on the MOF 1.4 metametamodel.)

    In any case, the 'XMI.TypeDefinitions' block is only used when encoding
    datatypes that are not part of the metamodel for the data being encoded.
    For PEAK applications, all such type definitions should be part of the
    model, and this is true for common UML usage as well.

    TODO

        Write Algorithm

          - needs to know composition link direction (needs peak.model support)

          - Element state will contain a reference to pseudo-DOM node, if
            available.  Elements are saved by modifying node in-place.
            Sub-elements are saved using their node, if the node's parent is
            the containing element's node.  If the sub-element has no node,
            save the sub-element (creating a node), and point its node's
            parent to the current element's node.

          - If the sub-element's node's parent is *not* the current element's
            node, create an 'xmi.idref' node linking to the sub-element node.

          - New elements, and non-persistent objects simply create a "fresh"
            node for use by the containing element.  Elements keep a reference
            to this new node, so that potential containers can tell if they've
            seen it.

          - We only care about keeping XMI.Extension tags contained directly
            in an element, in the top-level object list (XMI.content), and
            in the XMI.Extensions block.  If a node is modified, its extension
            tags may be moved to the end of the modified node's children.

          - Generate new ID's as UUIDs, and place in both UUID and ID fields;
            need to standardize on a '__uuid__' or similar field in elements
            so that elements that need/want a UUID to map over to/from another
            data system can do so.

          - Format transforms can be supported via DM.thunk(); it should be
            possible to copy an entire model from one DM to another in this
            way, and thus switch between XMI 1.0 and 1.1 (or other) storage
            formats.

          - For thunking to be effective, XMI.extensions must be sharable,
            and therefore immutable -- so we need an XMI extension/text class.

          - XMIDocument should become persistent, and use a second-order DM to
            load/save it.  Modifying XMINode instances should flag the
            XMIDocument as changed.  We can then implement a transactional
            file-based DM that can load and save the XMIDocument itself.

          - XMIDocument needs to know its version or select a strategy object
            to handle node updates for a particular XMI version.

          - Need to research 'ignorableWhitespace' et al to ensure that we can
            write cleanly indented files but with same semantics as originals.

        XMI 1.2

            XMI 1.2 is mostly a simplification and clarification of XMI 1.1:

                - Encoding of multi-valued attributes; note that it is not
                  permissible to have a value for a feature both in an
                  object tag's attribute and in the object's contained tags.

                - "Nested packages may result in name collision; a namespace
                  prefix is required in this case."  Need to review EBNF,
                  and "Namespace Qualified XML Element Names".  This may
                  require metadata support on the writing side.

        XMI 2.0

            * Requires full URI-based namespace handling; maybe we should
              go ahead and add this to current implementation?  Note that
              this means all the 'xmi.*' tag and attribute names are now
              'xmi:' instead.

            * Further note on namespace handling: it sounds as though
              XML attribute names for the target model are unqualified, and
              indeed that element names can be so as well.

            * Top-level element may not be the 'XMI' tag; if a document
              represents a single object and doesn't want to include the
              XMI documentation, it can simply add an 'xmi:version'
              attribute to the outermost tag representing the serialized
              object.

            * Compositions are less regular: instead of nesting object
              tags inside an attribute tag, the attribute and object tags
              can be combined.  The tag name is the attribute name, and a
              new 'xmi:type' attribute indicates the type of the object.
              If omitted, the type of the object is assumed to be the type
              specified by the composite reference.

            * Although 'xmi:id' is the normal ID attribute, it can be
              specified via a tagged value as being different.  It isn't
              clear how this would work if there were multiple ID attributes
              per XMI file.


        Other

          - metamodel lookups

          - cross-reference between files could be supported by having document
            objects able to supply a relative or absolute reference to another
            document.  But this requires HREF support.  :(  Note that
            cross-file HREF needs some way to cache the other documents and an
            associated DM, if it's to be dynamic.

"""





from peak.api import *
from peak.util import SOX
from weakref import WeakValueDictionary
from peak.persistence import Persistent
from xml.sax import saxutils
from types import StringTypes
from peak.model.api import TCKind, SimpleTC, Boolean, TypeCode
from kjbuckets import kjGraph

XMI_METAMODELS = PropertyName('peak.xmi.metamodels')

_any_converters = {

    'short': int,
    'long':  long,
    'ushort': int,
    'ulong': long,
    'float': float,
    'double': float,

    'boolean': Boolean.mdl_fromString,
    'char': str,
    'wchar': unicode,

    'octet': None, # XXX

    'longlong': long,
    'ulonglong': long,
    'longdouble': long,

    'string': str,
    'wstring': unicode,
}








_tc_mappings = [

    (TCKind.tk_short, 'XMI.CorbaTcShort'),
    (TCKind.tk_long, 'XMI.CorbaTcLong'),
    (TCKind.tk_ushort, 'XMI.CorbaTcUshort'),
    (TCKind.tk_ulong, 'XMI.CorbaTcUlong'),
    (TCKind.tk_float, 'XMI.CorbaTcFloat'),
    (TCKind.tk_double, 'XMI.CorbaTcDouble'),
    (TCKind.tk_boolean, 'XMI.CorbaTcBoolean'),
    (TCKind.tk_char, 'XMI.CorbaTcChar'),
    (TCKind.tk_wchar, 'XMI.CorbaTcWchar'),
    (TCKind.tk_octet, 'XMI.CorbaTcOctet'),
    (TCKind.tk_any, 'XMI.CorbaTcAny'),
    (TCKind.tk_TypeCode, 'XMI.CorbaTcTypeCode'),
    (TCKind.tk_Principal, 'XMI.CorbaTcPrincipal'),
    (TCKind.tk_null, 'XMI.CorbaTcNull'),
    (TCKind.tk_void, 'XMI.CorbaTcVoid'),
    (TCKind.tk_longlong, 'XMI.CorbaTcLongLong'),
    (TCKind.tk_ulonglong, 'XMI.CorbaTcUlongLong'),
    (TCKind.tk_longdouble, 'XMI.CorbaTcLongDouble'),
    (TCKind.tk_alias, 'XMI.CorbaTcAlias'),
    (TCKind.tk_struct, 'XMI.CorbaTcStruct'),
    (TCKind.tk_sequence, 'XMI.CorbaTcSequence'),
    (TCKind.tk_array, 'XMI.CorbaTcArray'),
    (TCKind.tk_objref, 'XMI.CorbaTcObjref'),
    (TCKind.tk_enum, 'XMI.CorbaTcEnum'),
    (TCKind.tk_union, 'XMI.CorbaTcUnion'),
    (TCKind.tk_except, 'XMI.CorbaTcExcept'),
    (TCKind.tk_string, 'XMI.CorbaTcString'),
    (TCKind.tk_wstring, 'XMI.CorbaTcWstring'),
    (TCKind.tk_fixed, 'XMI.CorbaTcFixed'),
]


type_kind_to_tag = dict(_tc_mappings)

type_tag_to_kind = dict([
    (tag,kind) for (kind,tag) in _tc_mappings
])


class XMINode(object):

    indexAttrs = 'xmi.uuid', 'xmi.id'

    __slots__ = [
        '_name','subNodes','allNodes','attrs','index','document',
        '__weakref__','parent','isExtension','ns2uri','uri2ns'
    ]


    def __init__(self, parent=None, name='',atts={}):
        self._name = name
        self.attrs = atts
        self.subNodes = []
        self.allNodes = []
        self.isExtension = (self._name=='XMI.extension')
        if parent is not None:
            self.index = parent.index
            self.document = parent.document
            self.parent = parent
            self.ns2uri = parent.ns2uri
            self.uri2ns = parent.uri2ns

    def _addNode(self,name,node):
        self.allNodes.append(node)
        self.subNodes.append(node)

    def _newNode(self,name,atts):
        return self.__class__(self,name,atts)

    def _addText(self,text):
        self.allNodes.append(text)

    def _finish(self):
        atts = self.attrs
        for a in self.indexAttrs:
            if atts.has_key(a):
                self.index[(a,atts[a])] = self
        return self


    def findNode(self,name):
        if self._name==name:
            return self
        for node in self.subNodes:
            f = node.findNode(name)
            if f is not None:
                return f


    def getId(self):
        atts = self.attrs
        for a in self.indexAttrs:
            if atts.has_key(a):
                return (a,atts[a])
        Id = None,id(self)
        self.index[Id] = self
        return Id


    def getRef(self):

        atts = self.attrs

        if 'href' in atts:
            raise NotImplementedError(
                "Can't handle href yet" #XXX
            )

        if 'xmi.uuidref' in atts:
            ref = 'xmi.uuid', atts['xmi.uuidref']

        elif 'xmi.idref' in atts:
            ref = 'xmi.id',  atts['xmi.idref']
        else:
            ref = self.getId()

        return self.index[ref].getId()

    def _setNS(self, ns2uri, uri2ns):
        self.ns2uri, self.uri2ns = ns2uri, uri2ns

    def getValue(self, feature, dm):

        atts = self.attrs

        if 'xmi.value' in atts:
            return feature.fromString(atts['xmi.value'])


        if not self.subNodes:
            return feature.fromString(''.join(self.allNodes))

        sub = self.subNodes

        if len(sub)==1:

            # XXX this assumes that feature is singular... and doesn't
            # XXX take into account the typecode expectations of the
            # XXX feature!  But we can't fix this until our UML metamodel
            # XXX is sound wrt datatypes.  :(

            child = sub[0]

            if not child._name.startswith('XMI.'):
                return dm[sub[0].getRef()]

            if child._name=='XMI.CorbaTypeCode':
                return child.getTypeCode(feature,dm)

            elif child._name=='XMI.any':
                return child.getAny(feature,dm)

        fields = []
        for node,f in zip(sub,feature.typeObject.mdl_features):
            if node._name <> 'XMI.field':
                raise ValueError("Don't know how to handle", node._name) #XXX
            fields.append(node.getValue(f,dm))

        return feature.fromFields(tuple(fields))



    def getTypeCode(self, feature, dm):

        sub = self.subNodes

        if len(sub)!=1:
            raise ValueError(
                "XMI.CorbaTypeCode tag must contain exactly one tag"
            )

        child = sub[0]
        tag = child._name
        kind = type_tag_to_kind.get(tag)

        if not kind:
            raise ValueError(
                "Don't know how to handle type code kind", tag
            )

        if kind in SimpleTC or kind==TCKind.tk_objref:
            return TypeCode(kind=kind)

        elif kind==TCKind.tk_alias:
            return TypeCode(
                kind=kind, content_type=child.getValue(feature,dm)
            )

        elif kind==TCKind.tk_struct:
            return child.getStructTypeCode(feature,dm)

        elif kind in (TCKind.tk_sequence,TCKind.tk_array):
            return TypeCode(
                kind=kind, content_type=child.getValue(feature,dm),
                length=int(child.attrs.get('xmi.tcLength',0))
            )

        elif kind==TCKind.tk_enum:
            return child.getEnumTypeCode(feature,dm)

        elif kind==TCKind.tk_union:
            return child.getUnionTypeCode(feature,dm)

        elif kind==TCKind.tk_except:
            return child.getExceptionTypeCode(feature,dm)

        elif kind in (TCKind.tk_string,TCKind.tk_wstring):
            return TypeCode(
                kind=kind, length=int(child.attrs.get('xmi.tcLength',0))
            )

        elif kind==TCKind.tk_fixed:
            return TypeCode(
                kind=kind,
                fixed_digits=int(child.attrs.get('xmi.tcDigits',0)),
                fixed_scale=int(child.attrs.get('xmi.tcScale',0))
            )

        raise AssertionError("Impossible typecode kind",kind)


    def getStructTypeCode(self, feature, dm):
        pass    # XXX


    def getEnumTypeCode(self, feature, dm):
        names = []
        for node in self.subNodes:
            if node._name == 'XMI.CorbaTcEnumLabel' \
                and 'xmi.tcName' in node.attrs:
                names.append(node.attrs['xmi.tcName'])
            else:
                raise ValueError('Invalid tag in enumeration typecode')
        return TypeCode(kind = TCKind.tk_enum, member_names = tuple(names))

    def getUnionTypeCode(self, feature, dm):
        pass    # XXX

    def getExceptionTypeCode(self, feature, dm):
        pass    # XXX




    def getAny(self, feature, dm):

        kind = self.attrs['xmi.type']
        converter = _any_converters.get(kind)

        if not converter or self.subNodes:
            raise ValueError("Can't handle non-primitive 'XMI.any' type",kind)

        return converter(''.join(self.allNodes))
































    def stateForClass(self, klass, dm):

        d = {}

        for attr,val in self.attrs.items():

            if attr.startswith('xmi.'): continue
            f = dm.getFeature(klass, attr)
            if f is None: continue

            if f.isReference:
                obs = [dm[('xmi.id',n)] for n in val.split()]
                if f.isMany:
                    d.setdefault(f.implAttr,[]).extend(obs)
                else:
                    d[f.implAttr], = obs    # XXX
            elif f.isMany:
                raise ValueError(
                    "Multi-valued feature coded as attribute",
                    attr, val
                )
            else:
                d[f.implAttr] = f.fromString(val)

        for node in self.subNodes:

            if node.isExtension: continue
            f = dm.getFeature(klass, node._name)
            if f is None: continue

            if f.isReference:
                obs = [dm[n.getRef()] for n in node.subNodes]
                if f.isMany:
                    d.setdefault(f.implAttr,[]).extend(obs)
                else:
                    d[f.implAttr], = obs    # XXX
            elif f.isMany:
                d.setdefault(f.implAttr,[]).append(node.getValue(f, dm))
            else:
                d[f.implAttr] = node.getValue(f, dm)

        coll = self.parent
        if coll is None: return d
        owner = coll.parent
        if owner is None: return d


        owner = dm[owner.getRef()]
        f = dm.getFeature(owner.__class__, coll._name)

        other = f.referencedEnd

        if other:

            f = getattr(klass,other)
            d['__xmi_parent_attr__'] = pa = f.implAttr

            if f.isMany:
                d.setdefault(pa,[owner])
            else:
                d.setdefault(pa,owner)

        return d



















    def writeTo(self, indStrm):

        write = indStrm.write; indStrm.push()

        try:
            write('<%s' % self._name.encode('utf-8'))
            for k,v in self.attrs.iteritems():
                write(' %s=%s' %
                    (k.encode('utf-8'), saxutils.quoteattr(v).encode('utf-8'))
                )

            if self.allNodes:
                write('>')
                if self.subNodes==self.allNodes:
                    write('\n'); indStrm.setMargin(1)
                    for node in self.subNodes:
                        node.writeTo(indStrm); write('\n')
                    indStrm.setMargin(-1)

                elif self.subNodes:
                    indStrm.setMargin(absolute=0)    # turn off indenting
                    # piece by piece...
                    for node in self.allNodes:
                        if isinstance(node,StringTypes):
                            write(saxutils.escape(node).encode('utf-8'))
                        else:
                            node.writeTo(indStrm)
                else:
                    indStrm.setMargin(absolute=0)    # turn off indenting
                    write(
                        saxutils.escape(''.join(self.allNodes)).encode('utf-8')
                    )

                write('</%s>' % self._name.encode('utf-8'))

            else:
                write('/>')

        finally:
            indStrm.pop()

class XMIDocument(binding.Component, XMINode):

    index = binding.Make(WeakValueDictionary)
    attrs = binding.Make(dict)
    subNodes = allNodes = binding.Make(list)
    _name = None
    parent = None
    ns2uri = {}
    uri2ns = kjGraph()

    document = binding.Obtain('.')
    nodeClass = XMINode

    version = binding.Make(lambda self: self.attrs['xmi.version'])


    def _newNode(self,name,atts):
        return self.nodeClass(self,name,atts)


    def _finish(self):

        self.index[()] = root = self.findNode('XMI.content')

        for sub in root.subNodes:
            sub.parent = None
        return self

    def writeTo(self, indStrm):
        indStrm.write('<?xml version="1.0" encoding="utf-8">\n')
        for node in self.subNodes:
            node.writeTo(indStrm)









    def metamodel(self):
        models = []
        for node in self.findNode('XMI.header').subNodes:
            if node._name == 'XMI.metamodel':
                if 'xmi.version' in node.attrs:
                    models.append('%(xmi.name)s.%(xmi.version)s' % node.attrs)
                else:
                    models.append(node.attrs['xmi.name'])

        if len(models)==1:
            return XMI_METAMODELS.of(self)[models[0]]

        raise ValueError("XMI file must have exactly one 'XMI.metamodel'")

    metamodel = binding.Make(metamodel)


























class DM(storage.StorableDM):

    resetStatesAfterTxn = False

    index     = binding.Obtain('document/index')
    metamodel = binding.Obtain('document/metamodel')
    document  = binding.Require("XMIDocument with data to use")

    def _ghost(self, oid, state=None):
        if oid==():
            return storage.PersistentQuery()
        target = self.index[oid]
        klass = self.getClass(target._name)
        if issubclass(klass,Persistent):
            return klass()
        ob = self.cache[oid] = klass()
        ob.__dict__.update(target.stateForClass(ob.__class__, self))
        return ob


    def getClass(self,name):
        name = name.split(':',1)[-1].replace('.','/')
        try:
            return getattr(self.metamodel, name.split('/')[-1])
        except AttributeError:
            return binding.lookupComponent(self.metamodel, './'+name)

    def getFeature(self,klass,name):    # XXX

        if ':' in name:
            name = name.split(':',1)[1]

        xm = getattr(klass,'_XMIMap',())

        if name in xm:
            return getattr(klass,xm[name],None)
        else:
            name = name.split('.')[-1]
            return getattr(klass,name,None)


    def _load(self, oid, ob):

        target = self.index[oid]

        if oid==():
            return [
                self[n.getRef()] for n in target.subNodes if not n.isExtension
            ]

        return target.stateForClass(ob.__class__, self)

def fromFile(filename_or_stream, parentComponent, **kw):
    document = XMIDocument(parentComponent)
    SOX.load(filename_or_stream, document, namespaces=True)
    return DM(parentComponent, document=document,**kw)[()]


























