#!/usr/bin/env python

'''
Use the Python DTrace consumer and run a syscall counter DTrace script with an
own aggregate walk function.

Created on Oct 10, 2011

@author: tmetsch
'''

from dtrace import DTraceConsumer

SCRIPT = 'syscall:::entry { @num[execname] = count(); }'


def my_walk(action, identifier, key, value):
    '''
    Aggregate walker.
    '''
    print '>', identifier, key, value


def main():
    '''
    Run DTrace...
    '''
    consumer = DTraceConsumer(walk_func=my_walk)
    consumer.run_script(SCRIPT, 4)

if __name__ == '__main__':
    main()
