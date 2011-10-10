#!/usr/bin/env python

'''
Use the Python DTrace consumer and run a syscall counter DTrace script.

Created on Oct 10, 2011

@author: tmetsch
'''

from ctypes import cast, c_char_p, c_int
from dtrace.consumer import DTraceConsumer, deref

script = 'syscall:::entry { @num[execname] = count(); }'

def my_walk(data, arg):
    '''
    Aggregate walker.
    '''
    tmp = data.contents.dtada_data
    name = cast(tmp + 16, c_char_p).value
    instance = deref(tmp + 272, c_int).value

    print '{0:4d} > {1:60s}'.format(instance, name)

    return 0

def main():
    consumer = DTraceConsumer()
    consumer.run_script(script, 4, walk_func=my_walk)

if __name__ == '__main__':
    main()
