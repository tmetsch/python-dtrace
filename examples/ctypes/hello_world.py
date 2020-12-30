#!/usr/bin/env python

"""
Use the Python DTrace consumer and run a Hello World DTrace script.

Created on Oct 10, 2011

@author: tmetsch
"""

from dtrace_ctypes import consumer

SCRIPT = 'dtrace:::BEGIN {trace("Hello World");}'


def main():
    """
    Run DTrace...
    """
    dtrace = consumer.DTraceConsumer()
    dtrace.run(SCRIPT)


if __name__ == '__main__':
    main()
