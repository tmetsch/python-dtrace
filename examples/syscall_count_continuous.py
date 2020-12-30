#!/usr/bin/env python

"""
Use the Python DTrace consumer as a Thread and run a syscall counter DTrace
script.

Created on Oct 10, 2011

@author: tmetsch
"""

import time

import dtrace

SCRIPT = 'syscall:::entry { @num[execname] = count(); }'


def main():
    """
    Run DTrace...
    """
    thr = dtrace.DTraceConsumerThread(SCRIPT)
    thr.start()

    # we will stop the thread after some time...
    time.sleep(5)

    # stop and wait for join...
    thr.stop()
    thr.join()


if __name__ == '__main__':
    main()
