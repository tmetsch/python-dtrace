#!/usr/bin/env python

'''
Use the Python DTrace consumer as a Thread and run a syscall counter DTrace
script.

Created on Oct 10, 2011

@author: tmetsch
'''

import time
from dtrace.ctypes.consumer import DTraceConsumerThread

SCRIPT = 'syscall:::entry { @num[execname] = count(); }'


def main():
    '''
    Run DTrace...
    '''
    dtrace = DTraceConsumerThread(SCRIPT)
    dtrace.start()

    # we will stop the thread after some time...
    time.sleep(2)

    # stop and wait for join...
    dtrace.stop()
    dtrace.join()

if __name__ == '__main__':
    main()
