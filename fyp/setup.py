#!/usr/bin/env python
# -*- coding: utf-8 -*-
from distutils.core import setup
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
