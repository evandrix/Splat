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

@mypkg.common.aspect_timer
def main():
    GLOBALS['byteorder'] = sys.byteorder

    # Part 0
    import mypkg.validator
    valid = mypkg.validator.main(GLOBALS)
    if not valid:
        print "USAGE: python %s [<path/package_name>|<.py{,c} file>]" % sys.argv[0]
        sys.exit(1)
    GLOBALS['basename'] = GLOBALS['pkg_name'].replace('/','.')
    if GLOBALS['basename'].startswith('.'): # no hidden
        GLOBALS['basename'] = GLOBALS['basename'][1:]

    print "(I): Bytecode scanner - classes+functions"
    import mypkg.scanner
    mypkg.scanner.main(GLOBALS)
#    mypkg.scanner.debug(GLOBALS)

    print "(II): Analyse function dependency"
    import mypkg.analyser_fn
    mypkg.analyser_fn.main(GLOBALS)
    mypkg.analyser_fn.debug(GLOBALS)

    print "(III): Analyse control flow (CFG)"
    import mypkg.analyser_cfg
    mypkg.analyser_cfg.main(GLOBALS)

    print "(V): Unit test generator"
    #

    mypkg.common.debug(GLOBALS)

if __name__ == "__main__":
    main()
