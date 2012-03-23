#!/usr/bin/env python
#-*- coding: utf-8 -*-
import sys
import time
import lxml.html
import urllib
import scrapy
BASE_URL   = 'http://pypi.python.org/pypi/'
SIMPLE_URL = 'http://pypi.python.org/simple/'
html = lxml.html.parse(SIMPLE_URL)
packages = html.xpath('//a/@href')
max_pkg_width = len(str(len(packages)))
max_pkg_name_width = max([len(p) for p in packages])
print >> sys.stderr, "Finished parsing index, found %d packages, width = %d chars" % (len(packages),max_pkg_name_width)
for i,a in enumerate(packages):
    sys.stderr.write('.')
    print "%s " % (\
    #(str(i).rjust(max_pkg_width,' '),
    urllib.unquote_plus(a[:-1]).ljust(max_pkg_name_width,' ')),
    pkg_url  = ''.join([BASE_URL,a])
    try:
        pkg_html = lxml.html.parse(pkg_url)
        sum = 0
        for elem in pkg_html.xpath('//td[@style]/text()'):
            if str(elem).isdigit():
                sum += int(elem)
        print sum,
    except IOError as e:
        continue
    finally:
        print
        sys.stdout.flush()
sys.exit(0)
