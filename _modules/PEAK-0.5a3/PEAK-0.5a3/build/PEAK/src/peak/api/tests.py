"""PEAK API test suite package.

    This only tests packages with an active and current test suite.
"""

allSuites = [
    'peak.binding.tests:test_suite',
    'peak.config.tests:test_suite',
    'peak.events.tests:test_suite',
    'peak.model.tests:test_suite',
    'peak.naming.tests:test_suite',
    'peak.query.tests:test_suite',
    'peak.running.tests:test_suite',
    'peak.security.tests:test_suite',
    'peak.storage.tests:test_suite',
    'peak.web.tests:test_suite',
]


def test_suite():
    from peak.util.imports import importSuite
    return importSuite(allSuites)

