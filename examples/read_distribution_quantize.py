#!/usr/bin/env python

'''
Use the Python DTrace consumer and run a syscall counter DTrace script.

Created on Mas 28, 2012

@author: tmetsch
'''

from dtrace import DTraceConsumer

# SCRIPT = 'io:::start { @bytes = quantize(args[0]->b_bcount); }'
SCRIPT = 'sysinfo:::readch { @dist[execname] = quantize(arg0); }'


def my_walk(id, key, values):
    print key
    for item in values:
        if item[0][0] > 0 and item[1] > 0:
            print '%8s %20s' % (item[0][0], item[1])


def main():
    '''
    Run DTrace...
    '''
    consumer = DTraceConsumer(walk_func=my_walk)
    consumer.run_script(SCRIPT, 10)

if __name__ == '__main__':
    main()

