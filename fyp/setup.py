#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from distutils.core import setup
py_version_t = sys.version_info[:2]
py_version_s = ".".join([str(x) for x in py_version_t])
assert py_version_s in ("2.7"), "Python version 2.7.x required"
setup(
    name='Automated Lazy Unit Testing in Python',
    version='1.0.0',
    author='Lee Wei Yeong',
    author_email='lwy08@doc.ic.ac.uk',
    packages=['fyp', 'fyp.mypkg', 'fyp.mypkg.test'],
    scripts=[],
    url='http://pypi.python.org/pypi/fyp/',
    license='LICENSE.txt',
    description='FYP project module',
    long_description=open('README.txt').read(),
)
