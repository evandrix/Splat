from peak.naming.api import *
from peak.util.uuid import UUID
from peak.api import model

class uuidURL(URL.Base):
    """
    draft-kindel-uuid-uri-00 UUID urls

    Attributes provided:

    uuid            a peak.util.uuid object
    quals           a tuple of (key, value) pairs of qualifiers
                    note that the meaning, syntax, and use of
                    qualifiers is not well defined.
    """

    supportedSchemes = 'uuid',

    class quals(URL.Collection):
        referencedType = model.Any
        syntax = URL.Tuple(URL.ExtractQuoted(),'=',URL.ExtractQuoted())
        separator = ';'

    class uuid(URL.Field):
        class referencedType(model.String):
            def mdl_normalize(klass,value):
                return UUID(value)

    syntax = URL.Sequence(
        uuid, (';', quals)
    )


