#!/usr/bin/env python

"""
Use the Python DTrace consumer with a script using quantize.

Created on Mar 28, 2012

@author: tmetsch
"""
from __future__ import print_function

import dtrace

# SCRIPT = 'io:::start { @bytes = quantize(args[0]->b_bcount); }'
SCRIPT = 'sysinfo:::readch { @dist[execname] = quantize(arg0); }'


def my_walk(_action, _identifier, key, values):
    """
    Walk the aggregrate.
    """
    print(key)
    for item in values:
        if item[0][0] > 0 and item[1] > 0:
            print('%8s %20s' % (item[0][0], item[1]))


def main():
    """
    Run DTrace...
    """
    consumer = dtrace.DTraceConsumer(walk_func=my_walk)
    consumer.run(SCRIPT, 10)


if __name__ == '__main__':
    main()
