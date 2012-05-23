#!/usr/bin/env python

"""Fuzz tester for the bytecode -> LLVM IR compiler.

The fuzzer implements two strategies for attacking the compiler:
  - Generate a random code object.
  - Take a known-good code object and change one byte to a random replacement.

Neither of these is a terribly sophisticated, but combined were sufficient to
expose multiple fatal errors in the compiler. Strategies that were tried, but
failed to find further problems:
  - Very large code objects with thousands of opcodes.
  - Take a known-good code object and shuffle the opcodes without fixing jump
    targets.
  - Take a known-good code object and shuffle the opcodes, fixing jump targets.
  - Take a known-good code object and replace opcodes with other valid opcodes
    (jump opcodes replace other jump opcodes, nullary opcodes replace other
    nullary opcodes, etc).

The code objects produced by these strategies would either be caught by the
JIT's bytecode validator or would be compiled successfully. The experience was
that the compiler has no trouble with syntactically-correct bytecode, even if
the semantics are invalid.

The fuzzer has yet to generate bytecode that causes problems for LLVM; all
errors so far have been in the bytecode -> LLVM IR frontend.

Example:
  /unladen/swallow/python jitfuzz.py --random_seed=12345678
"""

# Python imports
import opcode
import optparse
import random
import sys
import traceback
import types


def find_code_objects(*modules):
    """Find most code objects in the given modules."""
    for module in modules:
        for val in module.__dict__.itervalues():
            if isinstance(val, types.FunctionType):
                yield val.__code__
            if isinstance(val, type):
                for x in val.__dict__.values():
                    if isinstance(x, types.MethodType):
                        yield x.__code__


# These are known-good code objects for us to screw with.
CODE_OBJS = list(find_code_objects(traceback, optparse, random))

# The order of this list must match the order of parameters to types.CodeType().
CODE_ATTRS = ["argcount", "nlocals", "stacksize", "flags", "code",
              "consts", "names", "varnames", "filename", "name",
              "firstlineno", "lnotab", "freevars", "cellvars"]


def stderr(message, *args):
    print >>sys.stderr, message % args


def init_random_seed(random_seed):
    if random_seed == -1:
        random_seed = int(random.random() * 1e9)
    random.seed(random_seed)
    return random_seed


def clone_code_object(code_obj, **changes):
    """Copy a given code object, possibly changing some attributes.

    Example:
        clone_code_object(code, code=new_bytecode, flags=new_flags)

    Args:
        code_obj: baseline code object to clone.
        **changes: keys should be names in CODE_ATTRS, values should be the
          new value for that attribute name.

    Returns:
        A new code object.
    """
    members = []
    for attr in CODE_ATTRS:
        if attr in changes:
            members.append(changes[attr])
        else:
            full_attr = "co_" + attr
            members.append(getattr(code_obj, full_attr))
    return types.CodeType(*members)


def random_int(lower=0, upper=10):
    return random.randint(lower, upper)


def random_char(lower=1, upper=255):
    return chr(random.randint(lower, upper))


def random_string(length=None):
    if length is None:
        length = random_int(upper=5000)
    # Not random, but nothing looks at the contents of the strings.
    return "a" * length


def random_list(func, length=None):
    if length is None:
        length = random_int(upper=500)
    return [func() for _ in xrange(length)]


def random_object():
    return random.choice([None, True, 3e8, random_list,
                          "foo", u"bar", (9,), []])


def random_code_object():
    correct = (random.random() < 0.5)

    argcount = random_int()
    nlocals = random_int(upper=100)
    stacksize = random_int(upper=10000)
    flags = random_int(upper=1024)
    codestring = random_string()
    constants = tuple(random_list(random_object))
    names = tuple(random_list(random_string))
    filename = "attack-jit.py"
    name = random_string()
    firstlineno = random_int(lower=-1000, upper=1000)
    lnotab = ""
    freevars = tuple(random_list(random_string))
    cellvars = tuple(random_list(random_string))
    if correct:
        varnames = tuple(random_list(random_string, nlocals))
    else:
        varnames = tuple(random_list(random_string))

    code = types.CodeType(argcount, nlocals, stacksize, flags, codestring,
                          constants, names, varnames, filename, name,
                          firstlineno, lnotab, freevars, cellvars)
    return code


def permute_code_object(baseline):
    """Take a code object and change one byte of the bytecode."""
    bytecode = list(baseline.co_code)
    bytecode[random.randint(0, len(bytecode) - 1)] = random_char()
    return clone_code_object(baseline, code="".join(bytecode))


def generate_code():
    """Yield new code objects forever."""
    while True:
        if random.random() < 0.5:
            yield random_code_object()
        else:
            yield permute_code_object(random.choice(CODE_OBJS))


def attack_jit():
    # Track how many code objects are approved by the validator. If too many
    # are being rejected by the validator, we're not stressing LLVM enough.
    valid = 0
    rejected = 0
    for i, code in enumerate(generate_code()):
        code.co_use_jit = True
        try:
            code.co_optimization = 2
            valid += 1
        except:
            traceback.print_exc()
            rejected += 1
        if i % 100 == 0:
            print
            print "### %d attacks successfully repulsed" % i
            print "### Validated: %d; rejected: %d" % (valid, rejected)
            print


def main(argv):
    parser = optparse.OptionParser()
    parser.add_option("-r", "--random_seed",
        help="Random seed", type="int", default=-1)
    options, _ = parser.parse_args(argv)

    rand_seed = init_random_seed(options.random_seed)
    stderr("Using random seed: %s", rand_seed)
    attack_jit()


if __name__ == "__main__":
    main(sys.argv)