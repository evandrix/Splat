from nodeid48 import getnodeid48
from peak.util.random import rand16, randbytes
from time import time
from md5 import md5
from threads import allocate_lock

lasttime   = 0
offset     = 0
timelock   = allocate_lock()
begin_lock = timelock.acquire
end_lock   = timelock.release


__all__ = [
    'UUID',
    'DNS_NS', 'URL_NS', 'OID_NS', 'X500_NS', 'NIL_UUID'
]


try:
    from _uuidgen import uuidgen
except ImportError:
    try:
        from pywintypes import CreateGuid
        uuidgen = lambda: str(CreateGuid())[1:-1]
    except ImportError:
        try:
            from pythoncom import CreateGuid
            uuidgen = lambda: str(CreateGuid())[1:-1]
        except ImportError:
            uuidgen = None


def getClockSeq():
    return (rand16() & 0x3FFF) | 0x4000


clock_seq = getClockSeq()






class UUID(str):

    __slots__ = []

    def __new__(klass,
        from_string=None,
        name=None, ns=None, version=None, nodeid=None
        ):

        other_all_none = (name is None) and (ns is None) \
            and (version is None) and (nodeid is None)

        global lasttime, offset

        if uuidgen and other_all_none and not from_string:
            # just want any new id and can use the OS's generator
            from_string = uuidgen()

        if from_string:
            # Validate

            if not other_all_none:
                raise ValueError, "If string is specified, nothing else may be"

            from_string = from_string.lower()
            ok = 0
            parts = from_string.split('-')
            if len(parts) == 5:
                if [len(x) for x in parts] == [8, 4, 4, 4, 12]:
                    try:
                        # ensure it's all hex
                        long(''.join(parts), 16)
                        ok = 1
                    except:
                        pass

            if not ok:
                raise ValueError, "Illegal syntax for UUID: " + from_string



        else:
            if version is None:
                if name or ns:
                    version = 3
                else:
                    version = 1

            if version == 1:
                if nodeid is None:
                    nodeid = getnodeid48()
                else:
                    nodeid = nodeid.lower().replace(':','')
                    ok = 0
                    if len(nodeid) == 12:
                        try:
                            long(nodeid, 16)
                            ok = 1
                        except:
                            pass
                    if not ok:
                        raise ValueError, "Illegal node id: " + nodeid

                # Offset time value by a small (pseudo-)random number if a
                # repeated time() value occurs.  This algorithm should avoid
                # repeated UUID's for low-resolution system clocks, and yet
                # avoid "jumping the clock" for millisecond or better-resolution
                # clocks.  Assuming, of course, that you're not running this on
                # a machine where Python can run the entire constructor fifty
                # or more times per millisecond!

                begin_lock()

                try:
                    t = time()
                    if t==lasttime: offset += (rand16() % 191) + 1
                    else:           lasttime, offset = t, 0
                    ut = long(t * 10000000.0) + 0x01B21DD213814000L + offset

                finally:
                    end_lock()

                ut = "%015x" % ut

                from_string = "%s-%s-1%s-%04x-%s" % (
                    ut[7:], ut[3:7], ut[:3], clock_seq, nodeid
                )

            elif version == 3:
                if not name or not ns:
                    raise ValueError, "Both ns and name must be specified"

                if not isinstance(ns,UUID):
                    ns = UUID(ns)

                h = md5(ns.bytes() + name).digest()

            elif version == 4:
                h = randbytes(16, prng=0, wait=1)
                if h is None:
                    raise OSError, "Crypto-quality entropy not available"

            else:
                raise ValueError, "Only versions 1, 3, and 4 supported"


            if version == 3 or version == 4:
                h = [ord(c) for c in h]

                # insert the version
                h[6] = (h[6] & 0x0f) | (version << 4)

                # insert reserved bits
                h[8] = (h[8] & 0x3f) | 0x40

                h = ''.join(['%02x' % c for c in h])
                from_string = "%s-%s-%s-%s-%s" % (
                    h[:8], h[8:12], h[12:16], h[16:20], h[20:])

        return super(UUID, klass).__new__(klass, from_string)



    def bytes(self):
        """Return a 16 byte binary string representing the 128 bit ID in
        network order"""

        x = ''.join(self.split('-'))
        return ''.join([chr(int(x[i:i+2], 16)) for i in range(0, len(x), 2)])


    def base64(self):
        """Return a 24 byte string that is more compact than the
        36-byte hex form, but still not binary"""

        # slice is to remove the trailing newline
        return self.bytes().encode('base64')[:-1]


    def fromBytes(klass, s):
        if len(s) != 16:
            raise ValueError, "UUID byte representation must be 16 bytes long"

        s = tuple(["%02x" % ord(c) for c in s])
        s = "%s%s%s%s-%s%s-%s%s-%s%s-%s%s%s%s%s%s" % s

        return klass(s)

    fromBytes = classmethod(fromBytes)


    def fromBase64(klass, s):
        return klass.fromBytes(s.decode('base64'))

    fromBase64 = classmethod(fromBase64)


    def __repr__(self):
        return "UUID('%s')" % str(self)





# per draft-leach-uuids-guids-01

DNS_NS = UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')
URL_NS = UUID('6ba7b811-9dad-11d1-80b4-00c04fd430c8')
OID_NS = UUID('6ba7b812-9dad-11d1-80b4-00c04fd430c8')
X500_NS = UUID('6ba7b814-9dad-11d1-80b4-00c04fd430c8')

NIL_UUID = UUID('00000000-0000-0000-0000-000000000000')

































