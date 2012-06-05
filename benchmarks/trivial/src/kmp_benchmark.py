import random, time

bigstr = ''.join(map(lambda i:chr(random.randrange(32,127)), xrange(650000) ))
instr = ''.join(map(lambda i:chr(random.randrange(32,127)), xrange(3) ))
print 'Searching', instr, 'in', bigstr[:30]

t=time.clock()
i = 0
for f in KnuthMorrisPratt(bigstr,instr): i += 1
print 'Found',i,'times, in', time.clock()-t,'clocks'

t=time.clock()
i = 0
pos =0
while 1:
    pos = bigstr.find(instr)
    if pos<0:break
    i += 1
    bigstr = bigstr[pos+1:]
print 'Found',i,'times, in', time.clock()-t,'clocks'