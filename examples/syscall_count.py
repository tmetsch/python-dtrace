#!/usr/bin/env python

"""
Use the Python DTrace consumer and run a syscall counter DTrace script.

Created on Oct 10, 2011

@author: tmetsch
"""

from dtrace import DTraceConsumer

SCRIPT = 'syscall:::entry { @num[pid,execname] = count(); }'


def main():
    """
    Run DTrace...
    """
    consumer = DTraceConsumer()
    consumer.run(SCRIPT, 2)

if __name__ == '__main__':
    main()
