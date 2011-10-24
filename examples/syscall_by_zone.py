#!/usr/bin/env python

'''
Use the Python DTrace consumer and count syscalls by zone.

Created on Oct 10, 2011

@author: tmetsch
'''

from dtrace import DTraceContinuousConsumer
from threading import Thread
import threading
import time

SCRIPT = 'syscall:::entry { @num[zonename] = count(); }'


class MyThread(Thread):

    def __init__(self, script):
        Thread.__init__(self)
        self._stop = threading.Event()
        self.consumer = DTraceContinuousConsumer(script, walk_func=my_walk)

    def __del__(self):
        del(self.consumer)

    def run(self):
        Thread.run(self)

        while not self.stopped():
            time.sleep(1)  # self.consumer.sleep()
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


def my_walk(id, key, value):
    '''
    A simple aggregate walker.
    '''
    print 'Zone "{0:s}" made {1:d} syscalls.'.format(key[0], value)


def main():
    '''
    Run DTrace...
    '''
    print 'Hint: if you don\'t get any output try running it with pfexec...'

    thr = MyThread(SCRIPT)
    thr.start()

    # we will stop the thread after some time...
    time.sleep(5)

    # stop and wait for join...
    thr.stop()
    thr.join()

if __name__ == '__main__':
    main()
