from __future__ import generators
from peak.api import *
from connections import ManagedConnection, AbstractCursor, RowBase
from urllib import unquote
from interfaces import *
from peak.util.Struct import makeStructType
from peak.util.imports import importObject
from peak.naming.api import URL

__all__ = [
    'LDAPConnection', 'LDAPCursor', 'ldapURL', 'SCHEMA_PREFIX'
]

SCHEMA_PREFIX = PropertyName('peak.ldap.field_converters.*')

try:
    import ldap
    from ldap import SCOPE_BASE, SCOPE_ONELEVEL, SCOPE_SUBTREE

except:
    ldap = None
    SCOPE_BASE, SCOPE_ONELEVEL, SCOPE_SUBTREE = range(3)


scope_map = {'one': SCOPE_ONELEVEL, 'sub': SCOPE_SUBTREE, '': SCOPE_BASE}
scope_fmt = {SCOPE_ONELEVEL: 'one', SCOPE_SUBTREE: 'sub', SCOPE_BASE: ''}

def NullConverter(descr,value):
    return value












class LDAPCursor(AbstractCursor):

    """LDAP pseudo-cursor"""

    timeout      = -1
    msgid        = None
    bulkRetrieve = False
    attrs        = None
    defaultFormat= "ldap"

    disconnects = binding.Obtain(['import:ldap.SERVER_DOWN',])

    def close(self):

        if self.msgid is not None:
            self._conn.abandon(self.msgid)
            self.msgid = None

        super(LDAPCursor,self).close()


    def execute(self,dn,scope,filter='objectclass=*',attrs=None,dnonly=0):
        try:
            self.msgid = self._conn.search(dn,scope,filter,attrs,dnonly)
            if attrs:
                if 'dn' not in attrs:
                    attrs = ('dn',)+tuple(attrs)
                self.attrs = attrs

        except self.disconnects:
            self.errorDisconnect()

    def errorDisconnect(self):
        self.close()
        self.getParentComponent().close()
        raise

    def nextset(self):
        """LDAP doesn't do multi-sets"""
        return False


    def __iter__(self, onlyOneSet=True):

        msgid, timeout = self.msgid, self.timeout

        if msgid is None:
            raise ValueError("No operation in progress")

        getall = self.bulkRetrieve and 1 or 0
        fetch = self._conn.result

        attrs  = self.attrs or ()
        schema = SCHEMA_PREFIX.of(self)

        def getConverter(field):
            return importObject(schema.get(field,NullConverter), globals())

        conv = [(getConverter(f), f) for f in attrs]

        ldapEntry = makeStructType('ldapEntry',
            attrs, RowBase, __module__ = __name__,
        )

        mkTuple  = tuple.__new__
        fieldMap = ldapEntry.__fieldmap__

















        restype = None

        while restype != 'RES_SEARCH_RESULT':

            try:
                restype, data = fetch(msgid, getall, timeout)

            except self.disconnects:
                self.errorDisconnect()

            if restype is None:
                yield None  # for timeout errors

            for dn,m in data:

                m['dn']=dn

                fm=fieldMap.copy()
                fm.update(m)

                if len(fm)>len(fieldMap):
                    for k in m.keys():
                        if k not in fieldMap:
                            ldapEntry.addField(k)
                            conv.append( (getConverter(k),k) )

                yield mkTuple(ldapEntry,
                    [ c(f,m.get(f)) for (c,f) in conv ]
                )


        # Mark us as done with this query
        self.msgid = None








class LDAPConnection(ManagedConnection):

    protocols.advise(
        instancesProvide = [ILDAPConnection]
    )

    cursorClass = LDAPCursor



    def _open(self):

        address = self.address
        ext = address.extensions

        conn = ldap.open(address.host, address.port)

        if 'bindname' in ext and 'x-bindpw' in ext:
            conn.simple_bind_s(
                ext['bindname'][1], ext['x-bindpw'][1]
            )

        return conn


    def __getattr__(self, attr):
        return getattr(self.connection, attr)














class distinguishedName(naming.CompoundName):

    syntax = naming.PathSyntax(

        direction    = -1,      # DN's go right-to-left
        separator    = ',',     # are comma-separated
        trimblanks   = True,    # and blanks are ignored

        beginquote   = '"',     # LDAP uses double quotes for quoting, and
        multi_quotes = True,    #   can have multiple quoted strings per RDN.

        escape       = '\\',    # Escape character is backslash, but
        decode_parts = False,   #   don't try to unquote/unescape RDNs!

    )


























class ldapURL(URL.Base):

    """RFC2255 LDAP URLs, with the following changes:

    1) Additionally supports ldaps and ldapi (TLS and Unix Domain variants).

    2) Supports familiar (http, ftp-like) [user[:pass]@] syntax before
    the hostport part of the URL. These are translated into critical bindname
    and x-bindpw extensions. That is:

        ldap://foo:bar@localhost

    is treated as:

        ldap://localhost/????!bindname=foo,!x-bindpw=bar

    We do this for backwards compatability with some applications which
    used the old AppUtils LDAP module, and because the standard
    second syntax is quite unpleasant, especially when the bindname
    DN contains commas that would have to be quoted as %2C in the extensions.

    Attributes provided:

    host            hostname of server (or empty string)
    port            port number (integer, default 389)
    basedn          the dn provided (or empty string)
    attrs           tuple of attributes to retrieve, None if unspecified
    scope           SCOPE_BASE (default), SCOPE_ONELEVEL, or SCOPE_SUBTREE
    filter          search filter (or empty string)
    extensions      dictionary mapping extension names to tuples of
                    (critical, value) where critical is 0 or 1, and
                    value is a string.
    critical        a list of extension names that are critical, so
                    code may easily check for unsupported extenstions
                    and throw an error.
    """

    supportedSchemes = ('ldap', 'ldaps', 'ldapi')
    nameAttr = 'basedn'
    defaultFactory = 'peak.storage.LDAP.LDAPConnection'

    class host(URL.Field):
        pass

    class port(URL.IntField):
        defaultValue=389

    class basedn(URL.NameField):
        canBeEmpty = True
        referencedType = distinguishedName.asCompositeType()

    class attrs(URL.Field):
        syntax = URL.Repeat(
            URL.ExtractQuoted(URL.MatchString(pattern='[^?,]+')),
            separator = ','
        )

    class scope(URL.IntField):
        defaultValue = SCOPE_BASE
        syntax = URL.Conversion(
            canBeEmpty = True,
            converter = lambda x: scope_map[x.lower()],
            formatter = lambda x: scope_fmt[x],
        )

    class filter(URL.Field):
        canBeEmpty = True
        defaultValue = None














    class extensions(URL.Field):
        referencedType=model.Any    # XXX
        defaultValue={}
        syntax = URL.Conversion(
            URL.Repeat(
                URL.Tuple(
                    URL.ExtractQuoted(('!',)),  # optional '!' means critical
                    URL.ExtractQuoted(),'=',URL.ExtractQuoted()
                ),
                separator=','
            ),
            defaultValue={},
            converter=lambda x: dict([(k,(c and 1 or 0, v)) for (c,k,v) in x]),
            formatter=lambda d: [('!'[:c], k, v) for (k,(c,v)) in d.items()]
        )


    class critical(naming.URL.Field):
        referencedType=model.Any    # XXX
        defaultValue = ()


    syntax = naming.URL.Sequence(
        '//',
        (
            (URL.Named('_usr'), (':', URL.Named('_pw')), '@'), host, (':',port)
        ),
        ('/',basedn,
            ('?',attrs,
                ('?',scope,
                    ('?', filter,
                        ('?',extensions))))),
    )








    def parse(self, scheme, body):

        data = URL.parse(body, self.syntax)
        extensions = data.setdefault('extensions',{})

        if '_pw' in data:
            extensions['x-bindpw'] = (1, data['_pw'])
            del data['_pw']

        if '_usr' in data:
            extensions['bindname'] = (1, data['_usr'])
            del data['_usr']

        critical = [_k for (_k, (_crit, _v)) in extensions.items() if _crit]

        data['critical'] = tuple(critical)
        data['attrs'] = data.get('attrs') or None
        return data





protocols.declareAdapter(
    lambda url, proto: LDAPConnection(address=url),
    provides = [ILDAPConnection],
    forTypes = [ldapURL],
)













