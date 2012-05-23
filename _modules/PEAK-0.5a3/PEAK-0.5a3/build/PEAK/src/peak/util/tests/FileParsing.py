"""FileParsing tests"""

from unittest import TestCase, makeSuite, TestSuite
from peak.util.FileParsing import *


class LoggingParser(AbstractConfigParser):

    def __init__(self):
        self.log = []

    def add_setting(self, section, name, value, lineInfo):
        self.log.append( (section, name, value) )




























TEST_ONE = """
# these are comment lines at the top of
rem the anonymous section
; and should be ignored

[Section 1]

something = simple, no continuations

other: this has
    several
        continuation

    lines, including

    blanks.

oneMore = this has

# embedded comments that shouldn't show up

    in the middle.

[Section 2]

this = has
    # indented comments
    that should be part of the text
# but not this line!
"""

RESULT_ONE = [
    ('Section 1', 'something', 'simple, no continuations'),
    ('Section 1', 'other', 'this has\n'  'several\n'
                           'continuation\n\n'
                           'lines, including\n\nblanks.'),
    ('Section 1', 'oneMore', 'this has\n\n\nin the middle.'),
    ('Section 2', 'this',    'has\n# indented comments\n'
                             'that should be part of the text'),
]

class FormatTest(TestCase):

    def checkParsing(self):
        p = LoggingParser()
        p.readString(TEST_ONE)
        assert p.log == RESULT_ONE


TestClasses = (
    FormatTest,
)


def test_suite():
    s = []
    for t in TestClasses:
        s.append(makeSuite(t,'check'))

    return TestSuite(s)






















