===========================================
pyprimes -- generate and test prime numbers
===========================================


Introduction
------------

Compare a variety of algorithms for generating and testing prime numbers
with the pure-Python module ``pyprimes``.

Prime numbers are those positive integers which are not divisible exactly
by any number other than itself or one. Generating primes and testing for
primality has been a favourite mathematical pastime for centuries, as well
as of great practical importance for encrypting data.

Features of ``pyprimes``:

    - Produce prime numbers lazily, on demand.
    - Effective, fast algorithms including Sieve of Eratosthenes,
      Croft Spiral, and Wheel Factorisation.
    - Test whether numbers are prime efficiently.
    - Deterministic and probabilistic primality tests.
    - Examples of what *not* to do provided, including trial
      division, Turner's algorithm, and primality testing
      using a regular expression.
    - Factorise numbers into the product of prime factors.
    - Suitable for Python 2.5 through 3.2 from one code base.


Installation
------------

To install, extract the tarball into the current directory, then cd into the
expanded directory. Run:

    $ python setup.py install

to install.


Licence
-------

pyprimes is licenced under the MIT Licence. See the LICENCE.txt file and the
header of pyprimes.py.


Self-test and unit-tests
------------------------

You can run the module's doctests by executing the file from the commandline.
On most Linux or UNIX systems, change directories to the directory containing
the pyprimes.py file, then:

    $ chmod u+x pyprimes.py  # this is only needed once
    $ ./pyprimes.py

or:

    $ python pyprimes.py

If all the doctests pass, no output will be printed. To get verbose output,
run with the -v switch:

    $ python pyprimes.py -v


Known Issues
------------

See the CHANGES.txt file for a list of known issues.

