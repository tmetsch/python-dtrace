#!/usr/bin/env python

'''
Use the Python DTrace consumer with a script using lquantize.

Created on Mar 28 10, 2012

@author: tmetsch
'''

from dtrace import DTraceConsumer

SCRIPT = 'syscall::read:entry { @dist[execname] = lquantize(arg0, 0, 12, 2); }'


def my_walk(id, key, values):
    print key
    for item in values:
        if item[0][0] > 0:
            print '%8s %20s' % (item[0][0], item[1])


def main():
    '''
    Run DTrace...
    '''
    consumer = DTraceConsumer(walk_func=my_walk)
    consumer.run_script(SCRIPT, 5)

if __name__ == '__main__':
    main()

