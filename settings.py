import sys

MODULE_UNDER_TEST = 'program'
TRACE_DICT        = 'trace_params' # doesn't matter what goes here
SYS_MININT        = -sys.maxint-1
RECURSION_TIMEOUT = 10 #seconds

sys.setrecursionlimit(2**10)
