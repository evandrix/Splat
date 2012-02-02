# coding: utf-8

"""
This module provides command-line access to pystache.

Run this script using the -h option for command-line help.

"""

import json
# The optparse module is deprecated in Python 2.7 in favor of argparse.
# However, argparse is not available in Python 2.6 and earlier.
from optparse import OptionParser
import sys

# We use absolute imports here to allow use of this script from its
# location in source control (e.g. for development purposes).
# Otherwise, the following error occurs:
#
#   ValueError: Attempted relative import in non-package
#
from pystache.renderer import Renderer


USAGE = """\
%prog [-h] template context

Render a mustache template with the given context.

positional arguments:
  template    A filename or template string.
  context     A filename or JSON string."""


def parse_args(sys_argv, usage):
    """
    Return an OptionParser for the script.

    """
    args = sys_argv[1:]

    parser = OptionParser(usage=usage)
    options, args = parser.parse_args(args)

    template, context = args

    return template, context


def main(sys_argv):
    template, context = parse_args(sys_argv, USAGE)

    if template.endswith('.mustache'):
        template = template[:-9]

    renderer = Renderer()

    try:
        template = renderer.load_template(template)
    except IOError:
        pass

    try:
        context = json.load(open(context))
    except IOError:
        context = json.loads(context)

    rendered = renderer.render(template, context)
    print rendered


if __name__=='__main__':
    main(sys.argv)

