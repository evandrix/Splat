"""Extended Zope request classes to support language/charset negotiation"""

from zope.publisher import http, browser, xmlrpc, publish

__all__ = [
    'HTTPRequest', 'BrowserRequest', 'XMLRPCRequest', 'TestRequest'
]


class HTTPRequest(http.HTTPRequest, http.HTTPCharsets):

    """HTTPRequest with a built-in charset handler"""

    __slots__ = ()
    request = property(lambda self: self)


class BrowserRequest(
    browser.BrowserRequest, browser.BrowserLanguages, http.HTTPCharsets
):

    """BrowserRequest w/built-in charset and language handlers"""

    __slots__ = ()
    request = property(lambda self: self)


class XMLRPCRequest(xmlrpc.XMLRPCRequest, http.HTTPCharsets):

    """XMLRPCRequest w/built-in charset handler"""

    __slots__ = ()
    request = property(lambda self: self)








class TestRequest(
    browser.TestRequest, browser.BrowserLanguages, http.HTTPCharsets
):

    """TestRequest w/built-in charset and language handlers"""

    __slots__ = ()
    request = property(lambda self: self)


































