"""PEAK master test suite package.

Use with unittest.py to run all tests, or use the 'test_suite()' function
in an individual module to get just those tests."""


allSuites = [
    'protocols.tests:test_suite',
    'peak.api.tests:test_suite',
    'peak.metamodels.tests:test_suite',
    'peak.util.tests:test_suite',
    'peak.ddt.tests:test_suite',
]


def test_suite():
    from peak.util.imports import importSuite
    return importSuite(allSuites)


# shared, default config root for testing
_root = None

def testRoot():

    global _root

    if _root is None:
        from peak.api import config
        _root = config.makeRoot()

    return _root
