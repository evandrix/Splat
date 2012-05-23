"""Simple Objects from XML - quick-and-dirty XML parsing without a DOM

    This module implements most of the overhead needed for turning SAX
    events into a hierarchy of objects.  E.g., stack handling,
    delegation to node classes, etc.

    If all you need is to read an XML file and turn it into objects, you
    came to the right place.  If you need an actual model of the XML file
    that you can manipulate, with absolute fidelity to the original, you
    might be better off with a DOM, since this doesn't retain processing
    instructions or comments.

    SOX is faster than 'minidom' or any other DOM that I know of.  On the
    other hand, SOX is slower than PyRXP, but SOX handles Unicode correctly.

    To use this module, you will need a "document" object that implements
    either 'ISOXNode' or 'ISOXNode_NS', depending on whether you want
    namespace support.  The interfaces are very similar, except that
    the 'NS' version has some enhancements/simplifications that can't be
    added to the non-namespace version for backward-compatibility reasons.

    Once you have your document object, just call
    'SOX.load(filenameOrStream,documentObject,namespaces=flag)' to get back
    the result of your document object's '_finish()' method after it has
    absorbed all of the XML data supplied.

    If you need a simple document or node class, 'Document', 'Document_NS',
    'Node', and 'Node_NS' are available for subclassing or idea-stealing.
"""


from xml.sax import ContentHandler, parse
from xml.sax.saxutils import XMLGenerator
from protocols import Interface, advise
from kjbuckets import kjGraph

__all__ = [
    'load', 'ISOXNode', 'ISOXNode_NS', 'ObjectMakingHandler', 'NSHandler',
    'Node', 'Node_NS', 'Document', 'Document_NS', 'IndentedXML',
]

class ISOXNode(Interface):

    """Object mapping from an XML element

        Objects implementing ISOXNode are used to construct object structures
        from XML elements.  Each node gets to control how its subnodes are
        created, and what will be passed back to its parent node once its
        element subtree is complete.  In the simplest possible case, one can
        create a simple DOM-like tree of nodes which closely resemble the
        original XML.  Or, one can create a tree of objects with only minor
        structural similarities, or even use nodes just to do "side-effect"
        processing guided by the XML structures, like an interpretive parser.
    """

    def _newNode(name,attributeMap):
        """Create new child node from 'name' and 'attributeMap'

           Child node must implement the 'ISOXNode' interface."""

    def _acquireFrom(parentNode):
        """Parent-child relationship hook

           Called on newly created nodes to give them a chance to acquire
           context information from their parent node"""

    def _addText(text):
        """Add text string 'text' to node"""

    def _addNode(subObj):
        """Add finished sub-node 'subObj' to node"""

    def _finish():
        """Return an object to be used in place of this node in call to the
            parent's '_addNode()' method.  Returning 'None' will result in
            nothing being added to the parent."""






class ISOXNode_NS(Interface):

    def _newNode(name, attributeMap):

        """Create new child node from 'name' and 'attributeMap'

           Child node must implement the 'ISOX2Node' interface."""

    def _setNS(ns2uri, uri2ns):
        """Set namespace declaration maps"""

    def _addText(text):
        """Add text string 'text' to node"""


    def _addNode(subObj):
        """Add finished sub-node 'subObj' to node"""


    def _finish():
        """Return an object to be used in place of this node in call to the
            parent's '_addNode()' method.  Returning 'None' will result in
            nothing being added to the parent."""


















class ObjectMakingHandler(ContentHandler):

    """SAX handler that makes a pseudo-DOM"""

    def __init__(self,documentRoot):
        self.stack = [documentRoot]
        ContentHandler.__init__(self)

    def startElement(self, name, atts):
        top = self.stack[-1]
        node = top._newNode(name,atts)
        node._acquireFrom(top)
        self.stack.append(node)

    def characters(self, ch):
        self.stack[-1]._addText(ch)

    def endElement(self, name):
        stack = self.stack
        top = stack.pop()

        if top._name != name:
            raise SyntaxError,"End tag '%s' found when '%s' was wanted" % (name, top._name)

        out = top._finish()

        if out is not None:
            stack[-1]._addNode(name,out)

    def endDocument(self):
        self.document = self.stack[0]._finish()
        del self.stack









class NSHandler(ObjectMakingHandler):

    """Namespace-handling SAX handler; uses newer interface"""

    def __init__(self,documentRoot):

        ObjectMakingHandler.__init__(self,documentRoot)

        self.ns2uri = {}
        self.uri2ns = kjGraph()
        self.nsStack = []


    def startElement(self, name, atts):

        a = {}; prefix=None

        for k,v in atts.items():
            a[k]=v

            if k.startswith('xmlns'):

                rest = k[5:]

                if rest:
                    if rest[0]==':':
                        prefix=rest[1:]
                    else:
                        continue
                else:
                    prefix=''

                del a[k]
                self.add_prefix(prefix,v)

        top = self.stack[-1]
        node = top._newNode(name,a)
        self.stack.append(node)
        if prefix is not None: node._setNS(self.ns2uri, self.uri2ns)


    def add_prefix(self, prefix, uri):

        while len(self.nsStack) <= len(self.stack):
            self.nsStack.append( (self.ns2uri, self.uri2ns) )

        self.ns2uri = self.ns2uri.copy()
        self.ns2uri[prefix] = uri
        self.uri2ns = ~kjGraph( self.ns2uri.items() )


    def endElement(self, name):

        while len(self.nsStack) >= len(self.stack):
            self.ns2uri, self.uri2ns = self.nsStack.pop()

        ObjectMakingHandler.endElement(self, name)

























class Node:

    """Simple, DOM-like ISOXNode implementation"""

    advise( instancesProvide = [ISOXNode] )

    def __init__(self,name='',atts={},**kw):
        self._name = name
        self._subNodes = []
        self._allNodes = []
        self.__dict__.update(atts)
        self.__dict__.update(kw)

    def _addNode(self,name,node):
        self._allNodes.append(node)
        self._subNodes.append(node)
        d=self.__dict__
        if not d.has_key(name): d[name]=[]
        d[name].append(node)

    def _newNode(self,name,atts):
        return self.__class__(name,atts)

    def _addText(self,text):
        self._allNodes.append(text)

    def _get(self,name):
        return self.__dict__.get(name,[])

    def _findFirst(self,name):
        d=self._get(name)
        if d: return d
        for n in self._subNodes:
            if hasattr(n,'_findFirst'):
                d = n._findFirst(name)
                if d: return d

    def _finish(self):
        return self


    _acquiredAttrs = ()

    def _acquireFrom(self,parentNode):
        d=self.__dict__
        have=d.has_key
        for k in self._acquiredAttrs:
            if not have(k): d[k]=getattr(parentNode,k)


class Document(Node):

    def _finish(self):
        self.documentElement = self._subNodes[0]
        return self

    def _newNode(self,name,atts):
        return Node(name,atts)


class Node_NS(Node):

    ns2uri = {}
    uri2ns = kjGraph()

    def _newNode(self,name,atts):
        node = self.__class__(
            name, atts, ns2uri=self.ns2uri, uri2ns=self.uri2ns
        )
        return node

    def _setNS(self, ns2uri, uri2ns):
        self.ns2uri, self.uri2ns = ns2uri, uri2ns


class Document_NS(Node_NS):

    _finish = Document._finish.im_func

    def _newNode(self,name,atts):
        return Node_NS(name, atts)

def load(filename_or_stream, documentObject=None, namespaces=False):

    """Build a tree from a filename/stream, rooted in a document object"""

    if namespaces:

        if documentObject is None:
            documentObject = Document_NS()

        handler = NSHandler(documentObject)

    else:
        if documentObject is None:
            documentObject = Document()

        handler = ObjectMakingHandler(documentObject)

    parse(filename_or_stream, handler)
    return handler.document






















class IndentedXML(XMLGenerator):

    """SAX handler that writes its output to an IndentedStream"""

    def __init__(self, out=None, encoding="iso-8859-1"):
        if out is None:
            from IndentedStream import IndentedStream
            out = IndentedStream()
        XMLGenerator.__init__(self,out,encoding)

    def startElement(self,name,attrs):
        XMLGenerator.startElement(self,name,attrs)
        self._out.push(1)

    def startElementNS(self,name,qname,attrs):
        XMLGenerator.startElementNS(self,name,qname,attrs)
        self._out.push(1)

    def characters(self,content):
        self._out.push()
        self._out.setMargin(absolute=0)
        XMLGenerator.characters(self,content)
        self._out.pop()

    def endElement(self,name):
        self._out.pop()
        XMLGenerator.endElement(self,name)

    def endElementNS(self,name,qname):
        self._out.pop()
        XMLGenerator.endElementNS(self,name,qname)










