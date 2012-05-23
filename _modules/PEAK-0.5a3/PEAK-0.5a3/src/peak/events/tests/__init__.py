"""PEAK Event-driven programming test suite package

Use with unittest.py to run all tests, or use the 'test_suite()' function in
an individual module to get just those tests."""


allSuites = [
    'test_events:test_suite',
]

try:
    from twisted.internet.interfaces import IReactorCore
except ImportError:
    pass
else:
    allSuites.extend([
        'test_twisted:test_suite',
    ])

def test_suite():
    from peak.util.imports import importSuite
    return importSuite(allSuites, globals())

