#!/usr/bin/env python

'''
Use the Python DTrace consumer and count syscalls by zone.

Created on Oct 10, 2011

@author: tmetsch
'''

from dtrace import DTraceConsumerThread
from threading import Thread
import time

SCRIPT = 'syscall:::entry { @num[zonename] = count(); }'


def walk(id, key, value):
    '''
    Nice formatted aggregate walker.
    '''

    print 'Zone "{0:s}" made {1:d} syscalls.'.format(key[0], value)


def main():
    '''
    Run DTrace...
    '''
    print 'Hint: if you don\'t get any output try running it with pfexec...'

    consumer = DTraceConsumerThread(SCRIPT, walk_func=walk)
    dtrace = Thread(target=consumer.run)
    dtrace.start()

    # we will stop the thread after some time...
    time.sleep(5)

    # stop and wait for join...
    consumer.stop()
    dtrace.join()

if __name__ == '__main__':
    main()
