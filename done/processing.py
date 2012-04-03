import multiprocessing as mp
from multiprocessing import Process
from math import ceil, log

class PoolProcess( Process ):
    def __init__(self, rank, events, numproc, lock):
        mp.Process.__init__(self)
        self.rank = rank
        self.events = events
        self.numproc = numproc
        self.lock = lock

    def barrier(self):
        if self.numproc == 1: return

        # loop log2(num_threads) times, rounding up
        for k in range(int(ceil(log(self.numproc)/log(2)))):
            # send event to thread (rank + 2**k) % numproc
            receiver = (self.rank + 2**k) % self.numproc
            evt = self.events[ self.rank * self.numproc + receiver ]
            evt.set()
            # wait for event from thread (rank - 2**k) % numproc
            sender = (self.rank - 2**k) % self.numproc
            evt = self.events[ sender * self.numproc + self.rank ]
            evt.wait()
            evt.clear()

    def run(self):
        # print the rank of this process
        # synchronize access to stdout
        self.lock.acquire()
        print 'Hello World, I am process %d' % self.rank
        self.lock.release()

        # wait for the self.numproc - 1 other processes
        # to finish printing
        self.barrier()

        # print the rank of this process
        # synchronize access to stdout
        self.lock.acquire()
        print 'Hello World again, I am process %d' % self.rank
        self.lock.release()

if __name__ == '__main__':
    numproc = 4
    lock = mp.Lock()
    events = [mp.Event() for n in range(numproc**2)]
    pool = [PoolProcess(rank, events, numproc, lock) for rank in range(numproc)]
    for p in pool: p.start()
    for p in pool: p.join()
