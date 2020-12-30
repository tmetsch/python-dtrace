#!/usr/bin/env python

"""
Use the Python DTrace consumer and run a syscall counter DTrace script with an
own aggregate walk function.

Created on Oct 10, 2011

@author: tmetsch
"""

from __future__ import print_function
from ctypes import cast, c_char_p, c_int
from dtrace_ctypes import consumer

SCRIPT = 'syscall:::entry { @num[execname] = count(); }'


def my_walk(data, _):
    """
    Aggregate walker.

    Have a look at the simple walk func in the consumer source code...
    """
    tmp = data.contents.dtada_data
    name = cast(tmp + 16, c_char_p).value
    instance = consumer.deref(tmp + 272, c_int).value

    print('{0:4d} > {1:60s}'.format(instance, name.decode()))

    return 0


def main():
    """
    Run DTrace...
    """
    dtrace = consumer.DTraceConsumer(walk_func=my_walk)
    dtrace.run(SCRIPT, 4)


if __name__ == '__main__':
    main()
