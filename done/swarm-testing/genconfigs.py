#!/usr/bin/python

import sys
import string
import random

infile = sys.argv[1]
outfile = sys.argv[2]
count = int(sys.argv[3])

def pick(l):
    probs = []
    
    for o in l:
        if o[0].find("P:") == 0:
            probs.append (float(o[0][2:]))
            
    if len(probs) == 0:
        return random.choice(l)
    if len(probs) == len(l):
        pc = random.uniform(0,1)
        psum = 0.0;
        c = 0
        for p in probs:
            psum += p
            if pc <= psum:
                return (l[c])[1:]
            c += 1
        print "WARNING: Probabilities did not sum to 1.0"
        return random.choice(l)[1:] # In case you don't make probs add to 1, pick randomly!
    else:
        print "INVALID EXCLUSIVE CHOICE:  PROBABILITIES MISSING"            

excs = []
opts = []
ranges = []
reqalso = []
reqnever = []

curr = []

for line in open(infile):
    p = line.split()
    if p[0] == "EXC":
        if curr != []:
            excs.append(curr)
        curr = []
    elif p[0] == "OPT":
        if curr != []:
            excs.append(curr)
        curr = []
        opts.append(p[1:])
    elif p[0] == "RANGE":
        if curr != []:
            excs.append(curr)
        curr = []
        ranges.append(p[1:])
    elif p[0] == "REQUIRED-ALSO":
        if curr != []:
            excs.append(curr)
        curr = []
        reqalso.append(p[1:])
    elif p[0] == "REQUIRED-NEVER":
        if curr != []:
            excs.append(curr)
        curr = []
        reqnever.append(p[1:])
    else:
        curr.append(p)

if curr != []:
    excs.append(curr)

configs = set([])

while len(configs) < count:
    config = []
    for c in excs:
        for o in pick(c):
            config.append(o)
    for c in opts:
        if random.uniform(0,1) <= float(c[0]):
            for o in c[1:]:
                config.append(o)
    for c in ranges:
        if len(c) == 3:
            config.append(c[0] + " " + str(random.randint(int(c[1]), int(c[2]))))
        else:
            r = int(round(random.gauss(int(c[3]),int(c[4]))))
            while not ((r >= int(c[1])) and (r <= int(c[2]))):
                r = int(round(random.gauss(int(c[3]),int(c[4]))))
            config.append (" " + c[0] + " " + str(r))

    for r in reqalso:
        if r[0] in config:
            for r2 in r[1:]:
                if not r2 in config:
                    config.append(r2)

    cs = set([]) 

    for c in config:
        cs = cs | set([c])

    for r in reqnever:
        if r[0] in config:
            cs = cs - set(r[1:])


    sconfig = ""

    for c in cs:
        sconfig += " " + c




    cset = set([sconfig])
    configs = configs | cset

out = open(outfile,'w')
for c in configs:
    out.write(c)
    out.write("\n")
out.close()

    
