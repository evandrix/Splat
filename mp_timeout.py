import multiprocessing
import sys
import time
import logging
import settings
logger = multiprocessing.log_to_stderr()
logger.setLevel(logging.INFO)

class TimeoutException(Exception):
    pass
class RunableProcessing(multiprocessing.Process):
    def __init__(self, func, *args, **kwargs):
        self.queue = multiprocessing.Queue(maxsize=1)
        args = (func,) + args
        multiprocessing.Process.__init__(self, target=self.run_func, args=args, kwargs=kwargs)
    def run_func(self, func, *args, **kwargs):
        try:
            result = func(*args, **kwargs)
            self.queue.put((True, result))
        except Exception as e:
            self.queue.put((False, e))
    def done(self):
        return self.queue.full()
    def result(self):
        return self.queue.get()
def run(function, *args, **kwargs):
    now = time.time()
    proc = RunableProcessing(function, *args, **kwargs)
    proc.start()
    proc.join(settings.RECURSION_TIMEOUT)
    if proc.is_alive():
        proc.terminate()    # always force_kill process
        runtime = int(time.time() - now)
        raise TimeoutException('timed out after {0} seconds'.format(runtime))
    assert proc.done()
    success, result = proc.result()
    if success:
        return result
    else:
        raise result

def hanoi(height, start=1, end=3):
    steps = []
    if height > 0:
        helper = ({1, 2, 3} - {start} - {end}).pop()
        steps.extend(hanoi(height - 1, start, helper))
        steps.append((start, end))
        steps.extend(hanoi(height - 1, helper, end))
    return steps

if __name__ == "__main__":
    lasti = 0
    for i in xrange(sys.maxint):
        try:
            run(hanoi, i)
        except TimeoutException as e:
            print "last successful i: %d" % lasti
            break
        else:
            lasti=i
