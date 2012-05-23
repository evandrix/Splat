"""Tedious implementation details of name arithmetic used by peak.naming.names

Don't bother reading this unless you enjoy tedious details; you won't ever
need to use anything here directly."""

__all__ = [
    'name_add', 'name_radd', 'name_sub', 'name_rsub'
]

import names
from interfaces import COMPOUND_KIND, COMPOSITE_KIND, URL_KIND

def composite_plus_composite(n1,n2):

    l = list(n1)
    last = l.pop()

    if not last:
        l.extend(list(n2))
    else:
        l.append(last + n2[0])
        l.extend(list(n2)[1:])

    if len(l)==1 and l[0]:
        return l[0]

    return names.CompositeName(l)

def composite_plus_compound(n1,n2):

    l = list(n1)
    last = l.pop()

    if not last: l.append(n2)
    else:        l.append(last+n2)

    if len(l)==1 and l[0]:
        return l[0]

    return names.CompositeName(l)

def any_plus_url(n1,n2):
    return n2


def compound_plus_compound(n1,n2):
    return n1.__class__(list(n1)+list(n2))


def compound_plus_composite(n1,n2):

    l = list(n2)
    first = l[0]

    if first:   l[0] = n1+first
    else:       l[0] = n1

    if len(l)==1 and l[0]:
        return l[0]

    return names.CompositeName(l)


def url_plus_other(n1,n2):
    return n1.addName(n2)


name_addition = {
    (COMPOSITE_KIND,      URL_KIND): any_plus_url,
    (COMPOUND_KIND,       URL_KIND): any_plus_url,
    (URL_KIND,            URL_KIND): any_plus_url,
    (URL_KIND,       COMPOUND_KIND): url_plus_other,
    (URL_KIND,      COMPOSITE_KIND): url_plus_other,

    (COMPOSITE_KIND,COMPOSITE_KIND): composite_plus_composite,
    (COMPOUND_KIND,  COMPOUND_KIND): compound_plus_compound,
    (COMPOSITE_KIND, COMPOUND_KIND): composite_plus_compound,
    (COMPOUND_KIND, COMPOSITE_KIND): compound_plus_composite,
}



def name_add(self, other):
    if self and other:
        return name_addition[self.nameKind,other.nameKind](self,other)
    return self or other

def name_radd(self, other):
    if self and other:
        return name_addition[other.nameKind,self.nameKind](other,self)
    return self or other
































def same_minus_same(n1,n2):
    if not n2 or n1[:len(n2)] == n2:
        return n1[len(n2):]

def compound_minus_composite(n1,n2):
    if len(n2)==1:
        return n1-n2[0]

def composite_minus_compound(n1,n2):
    if n1:
        p = n1[0]-n2
        if p is not None:
            return names.CompositeName([p]+list(n1)[1:])


def url_minus_other(n1,n2):
    pass    # URL can't be a prefix of a name, or vice versa, so return 'None'


def url_minus_url(n1,n2):
    a1, nic1 = n1.getAuthorityAndName()
    a2, nic2 = n1.getAuthorityAndName()

    if a1==a2: return nic1 - nic2
    # else not subtractable, return None


name_subtraction = {
    (COMPOSITE_KIND,      URL_KIND): url_minus_other,
    (COMPOUND_KIND,       URL_KIND): url_minus_other,
    (URL_KIND,            URL_KIND): url_minus_url,
    (URL_KIND,       COMPOUND_KIND): url_minus_other,
    (URL_KIND,      COMPOSITE_KIND): url_minus_other,

    (COMPOSITE_KIND,COMPOSITE_KIND): same_minus_same,
    (COMPOUND_KIND,  COMPOUND_KIND): same_minus_same,
    (COMPOSITE_KIND, COMPOUND_KIND): composite_minus_compound,
    (COMPOUND_KIND, COMPOSITE_KIND): compound_minus_composite,
}


def name_sub(self, other):
    if other:
        return name_subtraction[self.nameKind,other.nameKind](self,other)
    return self


def name_rsub(self, other):
    if self:
        return name_subtraction[other.nameKind,self.nameKind](other,self)
    return other































