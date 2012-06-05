#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import sys
import time
import dis
import byteplay
import pydot
import inspect
import types
import mypkg.common
from mypkg.constants import *
from collections import defaultdict

f = lambda: defaultdict(f)
GLOBALS = defaultdict(f)

def recursive_print(v, lvl):
    if isinstance(v, dict):
        print '{'
        counter = 0
        for _k,_v in v.iteritems():
            if counter <= 3:
                if inspect.isclass(_k):
                    print '\t'*lvl+term.bold_blue_on_bright_green(_k.__name__)+':',
                else:
                    print '\t'*lvl+term.bold_blue_on_bright_green(str(_k))+':',
                if any(map(lambda cls: isinstance(_v, cls), [list,set,dict])) and len(_v) > 1:
                    recursive_print(_v, lvl+1)
                else:
                    print _v
                counter += 1
            else:
                print '\t'*lvl+'...','['+str(len(v))+']'
                break
        print '\t'*(max(0,lvl-1))+'}'
    elif isinstance(v, set):
        print list(v)[0],'...','['+str(len(v))+']'
    elif isinstance(v, list):
        print v[0],'...','['+str(len(v))+']'
    else:
        print '<hidden>'

def debug():
    if term.is_a_tty:
        print '===',term.underline('GLOBALS'), '==='
        for k,v in sorted(GLOBALS.iteritems()):
#            if k not in ['graph_fn_cfg']: continue
            if isinstance(v, basestring):
                print term.bold_cyan_on_bright_green(k) + ':',v
            else:
                print term.bold_cyan_on_bright_green(k) + ':',
                recursive_print(v,1)

@mypkg.common.aspect_timer
def main():
    # Part 0
    import mypkg.validator
    valid = mypkg.validator.main(GLOBALS)
    if not valid:
        print "USAGE: python %s [<path/package_name>|<.py{,c} file>]" % sys.argv[0]
        sys.exit(1)
    GLOBALS['basename'] = GLOBALS['pkg_name'].replace('/','.')
    if GLOBALS['basename'].startswith('.'):
        GLOBALS['basename'] = GLOBALS['basename'][1:]

    print "(I): Scanner - classes+functions"
    import mypkg.scanner
    mypkg.scanner.main(GLOBALS)
#    scanner.debug(GLOBALS)

    print "(II): Analyse function dependency"
    import mypkg.analyser_fn
    mypkg.analyser_fn.main(GLOBALS)
    mypkg.analyser_fn.debug(GLOBALS)

    print "(III): Analyse control flow (CFG)"
    import mypkg.analyser_cfg
    mypkg.analyser_cfg.main(GLOBALS)

    print "(IV): Unit test generator"

    debug()

if __name__ == "__main__":
    main()
