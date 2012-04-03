"""Miscellaneous Unicode and internationalization utilities"""

import codecs

__all__ = [ 'utf8orlatin1', 'utrunc', 'uopen', 'UnicodeO']

def utf8orlatin1(aStr):
    """
    Convert string 'aStr' to a unicode string. First, hope that it is utf8,
    but if it doesn't seem to be, assume it was latin1.
    """

    if isinstance(aStr,unicode):
        return astr

    try:
        return aStr.decode('utf8')
    except:
        return aStr.decode('latin1')


def utrunc(s, l):
    """
    Return an initial substring of 's' where
    the utf8 representation takes no more than l bytes

    Useful for safely truncating unicode strings for storage in utf8
    form in database fields that put an upper limit on length.
    """

    if isinstance(s,str):
        return s[:l]
    else:
        while l:
            s = s[:l]
            if len(s.encode('utf8')) <= l:
                return s
            else:
                l -= 1
        return s

def uopen(fn, mode='rb', encoding='utf8', errors='strict', buffering=1):
    """
    Open a file named by 'fn' with mode 'mode' whose contents are
    encoded using encoding (default utf8), where we will be
    reading and writing data as unicode strings
    """

    return codecs.open(fn, mode, encoding, errors, buffering)



class UnicodeO:
    """
    Like StringIO, but output only, and allows unicode strings for write()
    """

    def __init__(self, encoding):
        self.l = []
        self.encoding = encoding

    def write(self, data):
        if isinstance(data,str):
            data = data.decode(self.encoding)

        self.l.append(data)

    def getvalue(self):
        return u''.join(self.l)













