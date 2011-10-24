#!/usr/bin/env python

'''
Use the Python DTrace consumer as a Thread and run a syscall counter DTrace
script.

Created on Oct 10, 2011

@author: tmetsch
'''

from dtrace import DTraceContinuousConsumer
from threading import Thread
import threading
import time

SCRIPT = 'syscall:::entry { @num[execname] = count(); }'


class MyThread(Thread):

    def __init__(self, script):
        Thread.__init__(self)
        self._stop = threading.Event()
        self.consumer = DTraceContinuousConsumer(script)

    def __del__(self):
        del(self.consumer)

    def run(self):
        Thread.run(self)

        while not self.stopped():
            self.consumer.sleep()
            self.consumer.snapshot()

    def stop(self):
        '''
        Stop DTrace.
        '''
        self._stop.set()

    def stopped(self):
        '''
        Used to check the status.
        '''
        return self._stop.isSet()


def main():
    '''
    Run DTrace...
    '''
    thr = MyThread(SCRIPT)
    thr.start()

    # we will stop the thread after some time...
    time.sleep(5)

    # stop and wait for join...
    thr.stop()
    thr.join()

if __name__ == '__main__':
    main()
