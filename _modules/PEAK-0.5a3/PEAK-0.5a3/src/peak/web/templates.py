"""XML/XHTML Templates for 'peak.web', similar to Twisted's Woven

TODO

 - implement interaction wrapper for "/skin", "/request", etc. data paths

 - implement sub-template support (convert doc->DOMlet in another doc)

 - add hooks for DOMlets to validate the list of supplied parameters

 - 'list' DOMlet needs iteration variables, maybe paging

 - need translation DOMlets, among lots of other kinds of DOMlets

 - support DTD fragments, and the rest of the XML standard
"""

from __future__ import generators
from peak.api import *
from interfaces import *
from xml.sax.saxutils import quoteattr, escape
from publish import TraversalPath

__all__ = [
    'TEMPLATE_NS', 'DOMLETS_PROPERTY', 'DOMletParser', 'TemplateDocument'
]

TEMPLATE_NS = 'http://peak.telecommunity.com/DOMlets/'
DOMLETS_PROPERTY = PropertyName('peak.web.DOMlets')

unicodeJoin = u''.join

def infiniter(sequence):
    while 1:
        for item in sequence:
            yield item





class DOMletState(binding.Component):

    """Execution state for a DOMlet"""

    protocols.advise(
        instancesProvide = [IDOMletState],
    )

    write = binding.Require("Unicode output stream write() method")


    def findState(self, iface):

        """Find nearest DOMletState implementing 'iface'"""

        for c in config.iterParents(self):
            state = adapt(c,iface,None)
            if state is not None:
                return state






















class DOMletAsWebPage(binding.Component):

    """Render a template component"""

    protocols.advise(
        instancesProvide = [IWebPage],
        asAdapterForProtocols = [IDOMletNode],
        factoryMethod = 'fromNode'
    )

    templateNode = binding.Require("""Node to render""")

    def fromNode(klass, subject, protocol):
        return klass(templateNode = subject)

    fromNode = classmethod(fromNode)

    def render(self, context):
        myOwner = context.getParentComponent()
        data = []
        self.templateNode.renderFor(
            myOwner,
            DOMletState(
                myOwner, write=data.append
            )
        )
        return unicodeJoin(data)














class DOMletParser(binding.Component):

    """Parser that assembles a Document"""

    def parser(self):

        from xml.parsers.expat import ParserCreate
        p = ParserCreate()

        p.ordered_attributes = True
        p.returns_unicode = True
        p.specified_attributes = True

        p.StartDoctypeDeclHandler = self.startDoctype
        p.StartElementHandler = self.startElement
        p.EndElementHandler = self.endElement
        p.CharacterDataHandler = self.characters
        p.StartNamespaceDeclHandler = self.startNS
        p.EndNamespaceDeclHandler = self.endNS
        p.CommentHandler = self.comment

        # We don't use:
        # .StartNamespaceDeclHandler
        # .EndNamespaceDeclHandler
        # .XmlDeclHandler(version, encoding, standalone)
        # .ElementDeclHandler(name, model)
        # .AttlistDeclHandler(elname, attname, type, default, required)
        # .EndDoctypeDeclHandler()
        # .ProcessingInstructionHandler(target, data)
        # .UnparsedEntityDeclHandler(entityN,base,systemId,publicId,notationN)
        # .EntityDeclHandler(
        #      entityName, is_parameter_entity, value, base,
        #      systemId, publicId, notationName)
        # .NotationDeclHandler(notationName, base, systemId, publicId)
        # .StartCdataSectionHandler()
        # .EndCdataSectionHandler()
        # .NotStandaloneHandler()
        return p

    parser = binding.Make(parser)

    domlets = binding.Make(list) # "nearest explicit DOMlet" stack
    stack   = binding.Make(list) # "DOMlet being assembled" stack
    nsUri   = binding.Make(dict) # URI stack for each NS prefix

    myNs = binding.Make(        # prefixes that currently map to TEMPLATE_NS
        lambda self: dict(
            [(p,1) for (p,u) in self.nsUri.items() if u and u[-1]==TEMPLATE_NS]
        )
    )


    def parseFile(self, stream, document=None):
        if document is None:
            document = TemplateDocument(self.getParentComponent())
        self.stack.append(document)
        self.domlets.append(document)
        self.parser.ParseFile(stream)


    def comment(self,data):
        self.buildLiteral(u'<!--%s-->' % data)


    def startNS(self, prefix, uri):
        self.nsUri.setdefault(prefix,[]).append(uri)
        if uri==TEMPLATE_NS:
            self._delBinding('myNs')


    def endNS(self, prefix):
        uri = self.nsUri[prefix].pop()
        if uri==TEMPLATE_NS:
            self._delBinding('myNs')








    nsStack = binding.Make(list)

    def pushNSinfo(self,attrs):

        prefixes = []

        for i in range(0,len(attrs),2):

            k,v = attrs[i], attrs[i+1]

            if not k.startswith('xmlns'):
                continue

            rest = k[5:]
            if not rest:
                ns = ''
            elif rest.startswith(':'):
                ns = rest[1:]
            else:
                continue

            self.startNS(ns,v)
            prefixes.append(ns)

        self.nsStack.append(prefixes)


    def popNSinfo(self):
        map(self.endNS, self.nsStack.pop())












    def startElement(self, name, attrs):

        self.pushNSinfo(attrs)

        a = []
        append = a.append
        myNs = self.myNs or ('',)   # use unprefixed NS if no NS defined

        top = self.stack[-1]
        factory = top.tagFactory
        domletName = dataSpec = paramName = None

        for i in range(0,len(attrs),2):

            k,v = attrs[i], attrs[i+1]

            if ':' in k:
                ns, n = k.split(':',1)
            else:
                ns, n = '', k

            if n=='domlet' and ns in myNs:
                # XXX if domletName is not None or dataSpec is not None:
                # XXX     raise ???
                if ':' in v:
                    domletName, dataSpec = v.split(':',1)
                else:
                    domletName, dataSpec = v, ''

                if domletName:
                    factory = DOMLETS_PROPERTY.of(top)[domletName]
                    factory = adapt(factory, IDOMletElementFactory)

            elif n=='define' and ns in myNs:
                # XXX if paramName is not None:
                # XXX     raise ???
                paramName = v
            else:
                append((k,v))


        element = factory(top, tagName=name, attribItems=a,
            domletProperty = domletName or None,
            dataSpec  = dataSpec or '',
            paramName = paramName or None,
            # XXX nonEmpty=False
        )

        if paramName:
            self.domlets[-1].addParameter(paramName,element)

        if domletName:
            # New explicit DOMlet, put it on the explicit DOMlet stack
            self.domlets.append(element)
        else:
            # Push the previous "nearest enclosing explicit DOMlet"
            self.domlets.append(self.domlets[-1])

        self.stack.append(element)


    def endElement(self, name):
        self.domlets.pop()
        last = self.stack.pop()
        self.stack[-1].addChild(last)
        self.popNSinfo()


    def buildLiteral(self,xml):
        top = self.stack[-1]
        literal = top.literalFactory(top, xml=xml)
        top.addChild(literal)


    def characters(self, data):
        top = self.stack[-1]
        text = top.textFactory(top, xml=escape(data))
        top.addChild(text)




    def startDoctype(self, doctypeName, systemId, publicId, has_internal):

        if publicId:
            p = ' PUBLIC %s %s' % (quoteattr(publicId),quoteattr(systemId))
        elif systemId:
            p = ' SYSTEM %s' % quoteattr(systemId)
        else:
            p = ''

        # we ignore internal DTD subsets; they're not useful for HTML
        xml = u'<!DOCTYPE %s%s>\n' % (doctypeName, p)

        self.buildLiteral(xml)




























class Literal(binding.Component):

    """Simple static text node"""

    protocols.advise(
        classProvides = [IDOMletNodeFactory],
        instancesProvide = [IDOMletNode],
    )

    xml = u''

    staticText = binding.Obtain('xml')

    def renderFor(self, data, state):
        state.write(self.xml)


























class Element(binding.Component):

    protocols.advise(
        classProvides = [IDOMletElementFactory],
        instancesProvide = [IDOMletElement],
    )

    children       = binding.Make(list)
    params         = binding.Make(dict)

    tagName        = binding.Require("Tag name of element")
    attribItems    = binding.Require("Attribute name,value pairs")
    nonEmpty       = False
    domletProperty = None
    dataSpec       = binding.Make(lambda: '', adaptTo=TraversalPath)
    paramName      = None

    # IDOMletNode

    def staticText(self):

        """Note: replace w/staticText = None in dynamic element subclasses"""

        texts = [child.staticText for child in self.optimizedChildren]

        if None in texts:
            return None

        if texts or self.nonEmpty:
            texts.insert(0, self._openTag)
            texts.append(self._closeTag)
            return unicodeJoin(texts)
        else:
            return self._emptyTag

    staticText = binding.Make(staticText, suggestParent=False)





    def optimizedChildren(self):

        """Child nodes with as many separate text nodes combined as possible"""

        all = []
        texts = []

        def flush():
            if texts:
                all.append(
                    self.literalFactory(self, xml=unicodeJoin(texts))
                )
                texts[:]=[]

        for child in self.children:
            t = child.staticText
            if t is None:
                flush()
                all.append(child)
            else:
                texts.append(t)

        flush()
        return all

    optimizedChildren = binding.Make(optimizedChildren)


    def _traverse(self, data, state):

        return self.dataSpec.traverse(
            data, lambda ctx: self._wrapInteraction(ctx)
        ), state








    def renderFor(self, data, state):

        text = self.staticText
        if text is not None:
            state.write(text)
            return

        if not self.optimizedChildren and not self.nonEmpty:
            state.write(self._emptyTag)
            return

        if self.dataSpec:
            data, state = self._traverse(data, state)

        state.write(self._openTag)

        for child in self.optimizedChildren:
            child.renderFor(data,state)

        state.write(self._closeTag)


    def addChild(self, node):
        """Add 'node' (an 'IDOMletNode') to element's direct children"""

        if self._hasBinding('optimizedChildren'):
            raise TypeError(
                "Attempt to add child after rendering", self, node
            )
        self.children.append(node)


    def addParameter(self, name, element):
        """Declare 'element' as part of parameter 'name'"""

        self.params.setdefault(name,[]).append(element)





    # Override in subclasses

    def _wrapInteraction(self,interaction):
        # XXX This should wrap the interaction in an IWebTraversable simulator,
        # XXX which should include access to this element's parameters as well
        # XXX as interaction variables.
        raise NotImplementedError


    _emptyTag = binding.Make(
        lambda self: self._openTag[:-1]+u' />'
    )

    _closeTag = binding.Make(
        lambda self: u'</%s>' % self.tagName
    )

    _openTag = binding.Make(
        lambda self: u'<%s%s>' % ( self.tagName,
            unicodeJoin([
                u' %s=%s' % (k,quoteattr(v)) for (k,v) in self.attribItems
            ])
        )
    )

    tagFactory     = None # real value is set below
    textFactory    = Literal
    literalFactory = Literal

Element.tagFactory = Element











class TaglessElement(Element):

    """Element w/out tags"""

    _openTag = _closeTag = _emptyTag = ''


class TemplateDocument(TaglessElement):

    """Document-level template element"""

    parserClass = DOMletParser

    def parseFile(self, stream):
        parser = self.parserClass(self)
        parser.parseFile(stream,self)

























class ContentReplacer(Element):

    """Abstract base for elements that replace their contents"""

    staticText = None
    children   = optimizedChildren = binding.Obtain('contents')
    contents   = binding.Require("nodes to render in element body")

    def addChild(self, node):
        pass    # ignore children, only parameters count with us


class Text(ContentReplacer):

    """Replace element contents w/data (XML-quoted)"""

    def renderFor(self, data, state):
        if self.dataSpec:
            data, state = self._traverse(data, state)

        write = state.write
        write(self._openTag)
        write(escape(unicode(data.subject)))
        write(self._closeTag)


class XML(ContentReplacer):

    """Replace element contents w/data (XML structure)"""

    def renderFor(self, data, state):
        if self.dataSpec:
            data, state = self._traverse(data, state)

        write = state.write
        write(self._openTag)
        write(unicode(data.subject))
        write(self._closeTag)



class TaglessText(Text):

    """Text w/out open/close tag"""

    _openTag = _closeTag = _emptyTag = ''


class TaglessXML(XML):

    """XML w/out open/close tag"""

    _openTag = _closeTag = _emptyTag = ''





























class URLAttribute(Element):

    """Put the URL in an attribute"""

    staticText = None

    def renderFor(self, data, state):

        if self.dataSpec:
            data, state = self._traverse(data, state)

        url = unicode(data.absoluteURL)

        if not self.optimizedChildren and not self.nonEmpty:
            state.write(self._emptyTag % locals())
            return

        state.write(self._openTag % locals())
        for child in self.optimizedChildren:
            child.renderFor(data,state)
        state.write(self._closeTag)


class URLText(ContentReplacer):

    """Write absolute URL as body text"""

    def renderFor(self, data, state):

        if self.dataSpec:
            data, state = self._traverse(data, state)

        write = state.write

        write(self._openTag)
        write(unicode(data.absoluteURL))
        write(self._closeTag)




def URLTag(parentComponent, componentName=None, domletProperty=None, **kw):

    """Create a URLText or URLAttribute DOMlet based on parameters"""

    kw['domletProperty'] = domletProperty
    prop = (domletProperty or '').split('.')

    if len(prop)==1 or prop[-1]=='text':
        return URLText(parentComponent, componentName, **kw)

    elif prop[-1]=='notag':
        kw['_openTag'] = kw['_closeTag'] = ''
        return URLText(parentComponent, componentName, **kw)

    else:
        attrName = prop[-1].replace('+',':')
        attrs = [(k,v.replace('%','%%')) for (k,v) in kw.get('attribItems',())]
        d = dict(attrs)

        if attrName not in d:
            attrs.append((attrName,'%(url)s'))
        else:
            attrs = [
                tuple([k]+((k!=attrName) and [v] or ['%(url)s']))
                    for (k,v) in attrs
            ]

        kw['attribItems'] = attrs
        return URLAttribute(parentComponent, componentName, **kw)

protocols.adviseObject(URLTag, provides=[IDOMletElementFactory])










class List(ContentReplacer):

    def renderFor(self, data, state):

        if self.dataSpec:
            data, state = self._traverse(data, state)

        state.write(self._openTag)

        nextPattern = infiniter(self.params['listItem']).next
        allowed     = data.interaction.allows
        subcontext  = data.subcontext
        ct = 0

        # XXX this should probably use an iteration location, or maybe
        # XXX put some properties in execution context for loop vars?

        for item in data.subject:

            if not allowed(item):
                continue

            if not ct:
                for child in self.params.get('header',()):
                    child.renderFor(data,state)

            loc = subcontext(str(ct), item)
            nextPattern().renderFor(loc, state)
            ct += 1

        if not ct:
            # Handle list being empty
            for child in self.params.get('emptyList',()):
                child.renderFor(data, state)
        else:
            for child in self.params.get('footer',()):
                child.renderFor(data,state)

        state.write(self._closeTag)


