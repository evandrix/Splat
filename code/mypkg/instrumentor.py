#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement
import dis	    # disassembly
import marshal	# object serialisation
import types	# built-in types
import os	    # misc os interface
import sys	    # system-specific params & functions
import re	    # regex
import cli.app	# command-line tools
import time
import struct
import py_compile

# Bytecode instrumentor module #
# credits @ goo.gl/teUkT
#
# Features:
#   - hacks python bytecode (co_firstlineno, co_lnotab) to enhance line numbers,
#	to a more useful format 'orginial-relative-line-#{1,}_bytecode-offset{3}',
#	as source code is not made available
#   - idempotent transformation
#

class Instrumentor(object):
    """
        Input: 	<target>.pyc
        Output: <target>.pyc (instrumented)
    """

    def __init__(self, target):
        if not target.endswith(".pyc"):
            target += ".pyc"
        self.target = target

    def run(self):
        if isinstance(self.target, basestring):
            exit_code = False
            pyc = Instrumentor.PycFileObj(self.target)
            pyc.read()
            # do not modify more than once
            if not pyc.is_modified():
                pyc.modify()
                exit_code = True
            pyc.write()
            return exit_code

    class PycFileObj(object):
        SIGNATURE_BYTES = "\x00\xFF\x00\xFF\x00\xFF\x00"

        def __init__(self, filename):
            self.filename = filename

        def read(self):
            """
                Reads bytes from input .pyc file
                format described @ http://goo.gl/{ezIZ2, GXP77}
            """
            if isinstance(self.filename, basestring):
                with open(self.filename, "rb") as the_file:
                    # sizeof(magic_no, mod_ts) independent of 32/64bit
                    self.magic_no = the_file.read(4)    #4B
                    assert self.magic_no == py_compile.MAGIC
                    self.mod_ts   = the_file.read(4)    #modification timestamp
                    # decode timestamp = modification ts of compiled src
                    if struct.calcsize("i") == 4:
                        # 64-bit
                        unixtime = struct.unpack("i", self.mod_ts)[0]
                    elif struct.calcsize("L") == 4:
                        # 32-bit
                        unixtime = struct.unpack("L", self.mod_ts)[0]
                    #print >> sys.stderr, time.asctime(time.localtime(unixtime))
                    self.code     = marshal.load(the_file)  #code object

        def write(self):
            """
                Writes bytes into .pyc file
            """
            if isinstance(self.filename, basestring):
                module_name, _  = os.path.splitext(self.filename)
                dirname = os.path.dirname(self.filename)
                with open(os.path.join(dirname, '%s_instrumented.pyc'%module_name), "wb") as the_file:
                    assert self.magic_no == py_compile.MAGIC
                    the_file.write(self.magic_no)
                    the_file.write(self.mod_ts)
                    marshal.dump(self.code, the_file)
                    the_file.flush()

        def is_modified(self):
            return False

            module_name, _  = os.path.splitext(self.filename)
            dirname = os.path.dirname(self.filename)
            filename = os.path.join(dirname, '%s_instrumented.pyc'%module_name)
            with open(filename, "rb") as the_file:
                magic, moddate = the_file.read(4), the_file.read(4)
                code = marshal.load(the_file)
                return len(code.co_lnotab) > len(self.SIGNATURE_BYTES) and \
                    self.SIGNATURE_BYTES == \
                    code.co_lnotab[:len(self.SIGNATURE_BYTES)]

        def modify(self):
            def hack_line_numbers(code):
                """
                    Replace a code object's line number information so that every
                    byte of the bytecode is a new line. Returns a new code object.
                    Also recurses to hack the line numbers in nested code objects.
                """
                n_bytes    = len(code.co_code)
                new_consts = []
                lb_ranges  = [ord(code.co_lnotab[b*2]) \
                              for b in range(len(code.co_lnotab)/2)]
                lb_ranges.append(n_bytes - sum(lb_ranges))
                prev_lb    = -1 # invalid value
                new_lnotab = ''
                for lb in lb_ranges:
                    new_lnotab += self.SIGNATURE_BYTES
                    new_lnotab += chr(0xEB - prev_lb)
                    new_lnotab += "\x01\x01" * lb
                    prev_lb = lb
                for const in code.co_consts:
                    if type(const) == types.CodeType:
                        new_consts.append(hack_line_numbers(const))
                    else:
                        new_consts.append(const)

                return types.CodeType(
                    code.co_argcount, code.co_nlocals, code.co_stacksize,
                    code.co_flags, code.co_code, tuple(new_consts),
                    code.co_names, code.co_varnames, code.co_filename,
                    code.co_name, 0, new_lnotab)

            self.code = hack_line_numbers(self.code)

@cli.app.CommandLineApp
def main(app):
    target = app.params.target
    print "Instrumenting %s..." % target,
    instrumentor = Instrumentor(target)
    exit_code = instrumentor.run()
    print ("done!" if exit_code else "already instrumented!")

if __name__ == "__main__":
    # wrapper around argparse
    main.add_param("-t", "--target",
        help="specify target python bytecode file (*.pyc)", required=True)
    main.run()
