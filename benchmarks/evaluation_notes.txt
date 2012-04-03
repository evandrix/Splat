[7/3/12] Evaluation of `dexml` (example):
@ http://www.rfk.id.au/blog/entry/testing-better-coverage-tox/

$ g clone rfk / dexml
$ sloccount dexml/ | grep -C1 SLOC-by-Language
    Total # of lines = 1672
$ sloccount dexml/test.py | grep -C1 SLOC-by-Language
    Total # of lines for tests = 766
$ nosetests

I: 'coverage'
# coverage can only run python scripts
$ coverage run `which nosetests`
# only interested in coverage for dexml module, not coverage within tests themselves
$ coverage report --include="*dexml*" --omit="*test*"
# for html output
$ coverage html --include="*dexml*" --omit="*test*"

II: 'tox'
- automatic testing across python versions

