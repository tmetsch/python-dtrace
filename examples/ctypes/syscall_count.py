#!/usr/bin/env python

"""
Use the Python DTrace consumer and run a syscall counter DTrace script.

Created on Oct 10, 2011

@author: tmetsch
"""

from dtrace_ctypes.consumer import DTraceConsumer

SCRIPT = 'syscall:::entry { @num[execname] = count(); }'


def main():
    """
    Run DTrace...
    """
    consumer = DTraceConsumer()
    consumer.run(SCRIPT, 4)

if __name__ == '__main__':
    main()
