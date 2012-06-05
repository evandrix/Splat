#   Copyright 1999-2000 Michael Hudson mwh@python.net
#
#                        All Rights Reserved
#
#
# Permission to use, copy, modify, and distribute this software and
# its documentation for any purpose is hereby granted without fee,
# provided that the above copyright notice appear in all copies and
# that both that copyright notice and this permission notice appear in
# supporting documentation.
#
# THE AUTHOR MICHAEL HUDSON DISCLAIMS ALL WARRANTIES WITH REGARD TO
# THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS, IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL,
# INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER
# RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF
# CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
# CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import struct

class Label:
    def __init__(self,byte=None):
        self.byte=byte
        self.__op=None
        self.absrefs=[]
        self.relrefs=[]
    def resolve(self,code):
        self.__op=code.opcodes[code.byte2op[self.byte]].unflesh()
    def add_absref(self,byte):
        # request that the absolute address of self.op be written to
        # the argument of the opcode starting at byte in the
        # codestring
        self.absrefs.append(byte)
    def add_relref(self,byte):
        # request that the relative address of self.op be written to
        # the argument of the opcode starting at byte in the
        # codestring
        self.relrefs.append(byte)
    def __setattr__(self,attr,value):
        if attr == 'op':
            self.__op = value.unflesh()
        else:
            self.__dict__[attr] = value
    def __getattr__(self,attr):
        if attr == 'op':
            return self.__op
        else:
            raise AttributeError, attr
    def write_refs(self,cs):
        address=self.__op.byte
        for byte in self.absrefs:
            cs.seek(byte+1)
            cs.write(struct.pack('<h',address))
        for byte in self.relrefs:
            offset=address-byte-3
            cs.seek(byte+1)
            cs.write(struct.pack('<h',offset))

