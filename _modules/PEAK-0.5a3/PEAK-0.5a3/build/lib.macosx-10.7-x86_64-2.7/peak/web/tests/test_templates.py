"""Template tests

TODO

 - Mixed namespaces

 - DOMlet property redefinition within a component

 - Security used

 - DOCTYPE
"""

from unittest import TestCase, makeSuite, TestSuite
from peak.api import *
from peak.tests import testRoot
from cStringIO import StringIO


class TestApp(web.Traversable):

    security.allow(
        foo = security.Anybody,
        bar = security.Anybody,
        someXML = security.Anybody,
    )

    foo = "The title (with <xml/> & such in it)"

    bar = 1,2,3

    someXML = "<li>This has &lt;xml/&gt; in it</li>"

    show = binding.Require(
        "Template to dump this out with",
        permissionNeeded = security.Anybody
    )




class BasicTest(TestCase):

    template = open(config.fileNearModule(__name__,'template1.pwt')).read()

    rendered = """<html><head>
<title>Template test: The title (with &lt;xml/&gt; &amp; such in it)</title>
</head>
<body>
<h1>The title (with &lt;xml/&gt; &amp; such in it)</h1>
<ul><li>1</li><li>2</li><li>3</li></ul>
<ul><li>This has &lt;xml/&gt; in it</li></ul>
<ul><li>This has &lt;xml/&gt; in it</li></ul>
</body></html>"""

    def setUp(self):
        r = testRoot()
        app = TestApp(r, show = self.mkTemplate())
        self.interaction = web.TestInteraction(app)

    def mkTemplate(self):
        d = web.TemplateDocument(testRoot())
        d.parseFile(StringIO(self.template))
        return d

    def render(self):
        return self.interaction.simpleTraverse('show')

    def checkRendering(self):
        self.assertEqual(self.render(),self.rendered)












class NSTest(BasicTest):

    template = """<body xmlns:pwt="http://peak.telecommunity.com/DOMlets/">
<h1 pwt:domlet="text:foo">Title Goes Here</h1>
<ul pwt:domlet="list:bar">
    <li pwt:define="listItem" pwt:domlet="text"></li>
</ul>
</body>"""

    rendered = """<body xmlns:pwt="http://peak.telecommunity.com/DOMlets/">
<h1>The title (with &lt;xml/&gt; &amp; such in it)</h1>
<ul><li>1</li><li>2</li><li>3</li></ul>
</body>"""

TestClasses = (
    BasicTest, NSTest,
)

def test_suite():
    return TestSuite([makeSuite(t,'check') for t in TestClasses])





















