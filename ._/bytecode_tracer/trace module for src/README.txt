Tracing execution
    python -m trace --coverdir . --count --file coverage_report.dat main.py

Code coverage
    python -m trace --coverdir . --report --summary --missing --file coverage_report.dat main.py

Calling relationships
    python -m trace --listfuncs --trackcalls main.py
