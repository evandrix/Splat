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

import new

fleshable_dict_name = intern("$ forgot to call __init__ did we? $")
old_self_key = intern("$ weird obfuscated name $")

# this module implements some acquistion-style hacks for avoiding
# circular references. Unfortunately, it wegdes performance.

class Flesher:
    MagicSelfValue = [] # just something to have a unique id
    
    def __init__(self):
        setattr(self,fleshable_dict_name,{})
    def make_fleshed(self,attr_name,**data):
        attr = self.__dict__[attr_name]
        delattr(self,attr_name)
        getattr(self,fleshable_dict_name)[attr_name] = (attr,data)
    def __getattr__(self,attr_name):
        dict = self.__dict__[fleshable_dict_name]
        attr,data = dict.get(attr_name,(None,None))
        if attr is not None:
            return attr.flesh(data,owner=self)
        else:
            raise AttributeError, attr_name

class Fleshable:    
    def unflesh(self):
        return self.__dict__.get(old_self_key,self)
    def flesh(self,data=None,owner=None,**kw):
        if data is None:
            data = kw
        newdict = self.__dict__.copy()
        for k,v in data.items():
            if v is Flesher.MagicSelfValue:
                newdict[k] = owner
            else:
                newdict[k] = v
        if not newdict.has_key(old_self_key):
            newdict[old_self_key] = self
        return new.instance(self.__class__,newdict)
    def __setattr__(self,attr,value):
        selfd = self.__dict__
        if selfd.has_key(old_self_key):
            selfd[old_self_key].__dict__[attr] = value
        selfd[attr] = value
    # this next is called a *lot*
    def __getattr__(self,attr,
                    u=[],
                    error=AttributeError(),
                    old_self_key=old_self_key):
        if self.__dict__.has_key(old_self_key):
            dict = self.__dict__[old_self_key].__dict__
            if dict.has_key(attr):
                ret = dict[attr]
                self.__dict__[attr] = ret
                return ret
        error.args=(attr,)
        raise error
    def __cmp__(self,other):
        lid = id(getattr(self,old_self_key,self))
        rid = id(getattr(other,old_self_key,other))
        return lid - rid
    

class TF(Fleshable,Flesher):
    def __init__(self):
        self.s = self
        self.make_fleshed("s",s=self)

