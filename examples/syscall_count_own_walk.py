#!/usr/bin/env python

"""
Use the Python DTrace consumer and run a syscall counter DTrace script with an
own aggregate walk function.

Created on Oct 10, 2011

@author: tmetsch
"""
from __future__ import print_function

import dtrace

SCRIPT = 'syscall:::entry { @num[execname] = count(); }'


def my_walk(_action, identifier, key, value):
    """
    Aggregate walker.
    """
    print('>', identifier, key, value)


def main():
    """
    Run DTrace...
    """
    consumer = dtrace.DTraceConsumer(walk_func=my_walk)
    consumer.run(SCRIPT, 4)


if __name__ == '__main__':
    main()
