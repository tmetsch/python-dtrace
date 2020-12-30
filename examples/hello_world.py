#!/usr/bin/env python

"""
Use the Python DTrace consumer and run a Hello World DTrace script.

Created on Oct 10, 2011

@author: tmetsch
"""

import dtrace

SCRIPT = 'dtrace:::BEGIN {trace("Hello World"); exit(0);}'


def main():
    """
    Run DTrace...
    """
    consumer = dtrace.DTraceConsumer()
    # Even when the runtime is set to run 10sec this will terminate immediately
    # because of the exit statement in the D script.
    consumer.run(SCRIPT, runtime=10)


if __name__ == '__main__':
    main()
