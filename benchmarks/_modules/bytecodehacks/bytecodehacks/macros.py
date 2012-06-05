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

from bytecodehacks.macro import add_macro
def main():
    def setq((x),v):
        x = v
        return v
    add_macro(setq)

    def pre_incr((x)):
        x = x + 1
        return x
    add_macro(pre_incr)

    def post_incr((x)):
        t = x
        x = x + 1
        return t
    add_macro(post_incr)

    def pre_decr((x)):
        x = x - 1
        return x
    add_macro(pre_decr)

    def post_decr((x)):
        t = x
        x = x + 1
        return t
    add_macro(post_decr)

    def add_set((x),v):
        x = x + v
        return x
    add_macro(add_set)

    def sub_set((x),v):
        x = x - v
        return x
    add_macro(sub_set)

    def mul_set((x),v):
        x = x * v
        return x
    add_macro(mul_set)

    def div_set((x),v):
        x = x / v
        return x
    add_macro(div_set)

    def mod_set((x),v):
        x = x % v
        return x
    add_macro(mod_set)

main()

def test():
    from bytecodehacks.macro import expand

    def f(x):
        i = 0
        while pre_incr(i) < len(x):
            if setq(c, x[i]) == 3:
                print c, 42
    x = expand(f)
    return x
    x(range(10))
        
