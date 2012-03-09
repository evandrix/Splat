#!/usr/bin/env python

import time
import sys
import requests
from BeautifulSoup import BeautifulSoup

BASE_URL   = 'http://pypi.python.org/pypi/'
SIMPLE_URL = 'http://pypi.python.org/simple/'

r = requests.get(SIMPLE_URL)
soup = BeautifulSoup(r.content)
for i, a in enumerate(soup('a')):
    name = a.contents[0]
    url = BASE_URL + a.attrs[0][1]

    try:
        r = requests.get(url)
        package_soup = BeautifulSoup(r.content)
        try:
            values = (int(td.contents[0]) for td in package_soup('td', style='text-align: right;') if td.contents and td.contents[0].isdigit())
        except Exception:
            values = [-1]
    except Exception:
        values = [-2]
    print sum(values), name

print 'Fetched statistics from %d packages' % (i + 1)
