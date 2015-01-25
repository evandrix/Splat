In order to make swarm testing easier, two python utilities are
provided.  Swarm testing is easy enough to implement that you can
probably make your own swarm utilities if these don't serve your needs.

=========================================================================

cswarm.py

Usage:

cswarm.py <test-command> <config file> <# cores> <total test time in minutes>

<test-command> is the path an executable that generates, runs, and
checks tests.  it is expected that the executable will perform all
bookkeeping (say, storing coverage results or failing test runs)

<config file> contains the swarm configurations.  Each configuration
should be on a single line.  Configurations will be provided as
command-line arguments to the <test-command>.

<# cores> is the number of threads to start running tests.

<total test time in minutes> says how long you want to test -- each
thread will execute for that amount of time.


cswarm.py rtest rtest.configs5 5 10

where rtest.configs5 is:

--a --b --c
--a --b
--a --d
--c --b --d
--b --d

will spawn 5 threads, each of which will repeatedly run one of:

rtest --a --b --c
rtest --a --b
rtest --a --d
rtest --c --b --d
rtest --b --d

until 10 minutes of wall clock time have elapsed.

=========================================================================

genconfigs.py

Usage:

genconfigs.py <configuration definition file> <output file> <# configs>

Reads in a configuration definition file and produces <# configs>
unique configurations in <output file>.

The configuration definition file can use a few constructs to specify
the distribution from which configurations are drawn:

EXC
<option 1>
[<option 2>]
[<option 3>...]

-- EXC indicates a list of mutually-exclusive options, one of which will
be selected, without bias.

OPT <prob> <option 1> [<option 2>] [<option 3>...]

-- OPT, with probability <prob> includes all the options on the line

RANGE <option> <low> <high> [<avg> <std dev>]

-- RANGE always produces a value for <option>, which must need one
integer argument, between <low> and <high>; if <avg> and <std dev> are
provided, the distribution is Gaussian, otherwise simply a random
value between <low> and <high> inclusive.

REQUIRED-ALSO <option> <option 1> [<option 2>] [<option 3>...]

- REQUIRED-ALSO adds <option 1>... and others to any configurations
that are generated that include <option>

REQUIRED-NEVER <option> <option 1> [<option 2>] [<option 3>...]

- REQUIRED-NEVER removes <option 1>... and others from any
configurations that are generated that include <option>


Thus, the following configuration definition file:

EXC
--a
--b
--c
OPT 0.5 --d
OPT 0.1 --e
OPT 0.99 --f
RANGE --g 1 10
RANGE --h 1 1000 500 1
REQUIRED-ALSO --f --i --j

might generate a configuration such as:

--a --d --f --g 2 --h 501 --i --j