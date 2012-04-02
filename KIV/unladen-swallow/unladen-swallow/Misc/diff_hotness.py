#! /usr/bin/env python2.5

"""Compute the differences between two hotness metric tables.

When configured with --with-instrumentation, at interpreter-shutdown Python will
print, among other things, a table showing how hot the JIT judged various
functions to be. The format of this table is:
module_path:lineno (func_name) -> hotness_metric

If you copy and paste that table into a text file, this script can parse it for
you and tell what effect your changes to the hotness function is having.

$ python diff_hotness.py old_table.txt new_table.txt
### Newly-hot functions
	foo.py:9812 (startTagCloseP) now has 10343000 points

### No-longer-hot functions
	foo.py:1480 (endTagOther) had 108031 points

### Hotter functions
	bar.py:146 (consumeEntity) -> +14438 points
	foo:405 (charsUntil) -> +35 points

### Colder functions
	baz.py:131 (elementInScope) -> -7403 points
	baz.py:201 (elementInActiveFormattingElements) -> -5916 points
"""

from __future__ import with_statement

__author__ = "collinwinter@google.com (Collin Winter)"

# Python imports
import optparse
import re
import sys


# function_id -> hotness_metric
PARSE_LINE = re.compile(r"^(.+)\s+->\s+(\d+)$")

def parse_table(table_data):
    """Parse a hotness table into its constituent pieces.

    Args:
        table_data: string representing the hotness table, one function per
            line.

    Returns:
        Dict mapping function_id (str) to hotness metric (int).

    Raises:
        ValueError: if a line in the file was improperly formatted.
    """
    table = {}
    for i, line in enumerate(table_data.splitlines()):
        match = PARSE_LINE.match(line)
        if match:
            function_id, hotness_metric = match.groups()
            table[function_id] = int(hotness_metric)
        else:
            raise ValueError("Bad input at line %d: %r" % (i, line))
    return table


class DiffSummary(object):
    """Summary of the differences between two hotness tables.

    Attributes (all dicts mapping function ids to ints):
        appeared: newly-hot functions; how hot are they now?
        disappeared: which functions are no longer hot; how hot were they?
        hotter: how much hotter are these functions than they were?
        colder: how much colder are these functions than they were?
    """

    def __init__(self):
        self.appeared = {}
        self.disappeared = {}
        self.hotter = {}
        self.colder = {}


def diff_tables(base_table, new_table):
    """Compute the difference between the old and new hotness tables.

    Args:
        base_table: dict from parse_table().
        new_table: dict from parse_table().

    Returns:
        DiffSummary instance.
    """
    results = DiffSummary()

    # Search for functions that either appeared or disappeared based on the
    # hotness function change.
    base_funcs = set(base_table)
    new_funcs = set(new_table)
    for func in (new_funcs - base_funcs):
        results.appeared[func] = new_table[func]
    for func in (base_funcs - new_funcs):
        results.disappeared[func] = base_table[func]

    # Search for functions that became hotter or colder based on the hotness
    # function change.
    common_funcs = base_funcs & new_funcs
    for func in common_funcs:
        diff = new_table[func] - base_table[func]
        if diff > 0:
            results.hotter[func] = diff
        elif diff < 0:
            results.colder[func] = diff

    return results


def main(argv):
    parser = optparse.OptionParser(
        usage="%prog base_hotness new_hotness",
        description=("Diff two hotness function tables."))
    options, args = parser.parse_args()

    if len(args) != 2:
        parser.error("Need to specify two hotness tables")
    base_filename, new_filename = args

    with open(base_filename) as base_file:
        base_data = parse_table(base_file.read())
    with open(new_filename) as new_file:
        new_data = parse_table(new_file.read())

    differences = diff_tables(base_data, new_data)
    if differences.appeared:
        print "### Newly-hot functions"
        for func, hotness in differences.appeared.items():
            print "\t%s now has %d points" % (func, hotness)
        print
    if differences.disappeared:
        print "### No-longer-hot functions"
        for func, hotness in differences.disappeared.items():
            print "\t%s had %d points" % (func, hotness)
        print
    if differences.hotter:
        print "### Hotter functions"
        for func, diff in differences.hotter.items():
            print "\t%s -> +%d points" % (func, diff)
        print
    if differences.colder:
        print "### Colder functions"
        for func, diff in differences.colder.items():
            print "\t%s -> %d points" % (func, diff)
        print


if __name__ == "__main__":
    main(sys.argv)
