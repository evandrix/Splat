#!/usr/bin/env python

import os
import sys
from glob import glob
from optparse import OptionParser

import cc

USAGE = 'usage: %prog [options] *.py'
VERSION = 'Sat Aug 21 version with support for overall complexity (http://aufather.wordpress.com)'


def parse_cmd_args():
    from optparse import OptionParser

    parser = OptionParser(usage=USAGE, version=VERSION)
    parser.add_option('-c', '--complexity', dest='complexity',
            action='store_true', default=False,
            help='print complexity details for each file/module')
    parser.add_option('-t', '--threshold', dest='threshold',
            type='int', default=7,
            help='threshold of complexity to be ignored (default=7)')
    parser.add_option('-a', '--all', dest='allItems',
            action='store_true', default=False,
            help='print all metrics')
    parser.add_option('-s', '--summary', dest='summary',
            action='store_true', default=False,
            help='print cumulative summary for each file/module')
    parser.add_option('-r', '--recurs', dest='recurs',
            action='store_true', default=False,
            help='process files recursively in a folder')
    parser.add_option('-d', '--debug', dest='debug',
            action='store_true', default=False,
            help='print debugging info like file being processed')
    parser.add_option('-o', '--outfile', dest='outFile',
            default=None,
            help='output to OUTFILE (default=stdout)')
    options, args = parser.parse_args()

    if (options.allItems):
        options.complexity = True
        options.summary = True

    return (options, args)


class FileList(object):
    '''Get set of files recursively'''
    def __init__(self, args, recurs=False):
        self.args = args
        self.recurs = recurs
        self.files = set()
        self.getAll()

    def getAll(self):
        for arg in self.args:
            arg = os.path.expandvars(os.path.expanduser(arg))
            if os.path.isdir(arg):
                self.getDirs(arg)
            elif os.path.isfile(arg):
                self.getFiles(arg)
            else:
                self.getPackages(arg)

    def getDirs(self, name):
        if self.recurs:
            self.getDirsRecursively(name)
            return

        for f in glob(os.path.join(name, '*.py')):
            if os.path.isfile(f):
                self.files.add(os.path.abspath(f))

    def getDirsRecursively(self, name):
        for root, folders, files in os.walk(name):
            for f in files:
                if f.endswith(".py"):
                    self.files.add(os.path.abspath(os.path.join(root, f)))

    def getFiles(self, name):
        if name.endswith(".py"):
            # only check for python files
            self.files.add(os.path.abspath(name))

    def getPackages(self, name):
        join = os.path.join
        exists = os.path.exists
        partial_path = name.replace('.', os.path.sep)
        for p in sys.path:
            path = join(p, partial_path, '__init__.py')
            if exists(path):
                self.files.add(os.path.abspath(path))
            path = join(p, partial_path + '.py')
            if exists(path):
                self.files.add(os.path.abspath(path))
        raise Exception('invalid module')


def print_fail_files(fail, outFile=sys.stdout):
    if len(fail):
        outFile.write("Totally %d files failed\n" % len(fail))
        for f in fail:
            outFile.write("FAILED to process file: %s\n" % f)


def main():
    options, args = parse_cmd_args()
    files = FileList(args, options.recurs).files
    outFile = sys.stdout
    fail = set()
    if options.outFile:
        outFile = open(options.outFile, 'w')
    pp = cc.PrettyPrinter(outFile, options.complexity,
                          options.threshold, options.summary)
    sumStats = cc.FlatStats()
    for f in files:
        if options.debug:
            print "File being processed: ", f
        code = open(f).read() + '\n'
        stats = cc.measure_complexity(code, f)
        if not stats:
            fail.add(f)
            continue
        sumStats = sumStats + stats
        pp.pprint(f, stats)
    outFile.write("Total Cumulative Statistics\n")
    outFile.write(str(sumStats))
    outFile.write('\n')
    print_fail_files(fail, outFile)

if __name__ == '__main__':
    main()

