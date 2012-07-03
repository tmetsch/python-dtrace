#!/usr/bin/env python

'''
Use the Python DTrace consumer and count syscalls by zone.

Created on Oct 10, 2011

@author: tmetsch
'''

from dtrace import DTraceConsumerThread
import time

SCRIPT = 'syscall:::entry { @num[zonename] = count(); }'


def my_walk(action, identifier, key, value):
    '''
    A simple aggregate walker.
    '''
    print 'Zone "{0:s}" made {1:d} syscalls.'.format(key[0], value)


def main():
    '''
    Run DTrace...
    '''
    thr = DTraceConsumerThread(SCRIPT, walk_func=my_walk, sleep=1)
    thr.start()

    # we will stop the thread after some time...
    time.sleep(5)

    # stop and wait for join...
    thr.stop()
    thr.join()

if __name__ == '__main__':
    main()
