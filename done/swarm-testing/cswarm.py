#!/usr/bin/python

import subprocess
import threading
import time
import sys

class ThreadSwarm(threading.Thread):
    def __init__(self, configs, n):
        threading.Thread.__init__(self)
        self.configs = configs
        self.n = n

    def run(self):
        rstart = time.time()
        cbudget = budget / len(self.configs)
        t = 0
        for c in self.configs:
            print "(START) " + str(c) + " budget " + str(cbudget)
            start = time.time()
            current = time.time()
            tc = 0
            while (current - start) < cbudget:
                prefix = str(self.n) + "." + str(t)
                subprocess.call([run, prefix] + c)
                t = t + 1
                tc = tc + 1
                current = time.time()
                if (current - rstart) > budget:
                    print "OVER BUDGET, TERMINATING THREAD"
                    totals.append(tc)
                    return

            print ("(DONE) " + str(c) + " " + str (tc) + " tests")
            totals.append(tc)
                                
print "USAGE: cswarm.py <test-command> <config file> <# cores to use> <total test time in minutes>"

run = sys.argv[1]
cfile = sys.argv[2]
procs = int(sys.argv[3])
budget = float(sys.argv[4]) * 60.0 # Expected to be in minutes

configs = []
for c in range(procs):
    configs.append([])

proc = 0
for line in open(cfile):
    args = line.split()
    configs[proc].append (args)
    proc = (proc + 1) % procs

totals = []
threads = []

n = 0
for s in configs:
    if (s == []):
        s = configs[0]
    t = ThreadSwarm(s, n)
    t.start()
    threads.append(t)
    n += 1

alive = True
while alive:
    alive = False
    for t in threads:
        if t.isAlive():
            alive = True

print "All tests on all configurations complete."

total = 0
for t in totals:
    total += t

print (str(total) + " total tests")
