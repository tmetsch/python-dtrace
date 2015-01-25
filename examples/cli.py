#!/usr/bin/env python

"""
A CLI for Dtrace which acts almost like the normal dtrace command on your
shell.

Created on Apr 11, 2012

@author: tmetsch
"""

from dtrace import DTraceConsumerThread
import sys


def print_lquantize(values):
    """
    Print a lquantize.
    """
    # find max
    maxi = 0
    for item in values:
        if item[1] > maxi:
            maxi = item[1]

    for item in values:
        if item[0][0] > 0:
            print '%10s ' % item[0][0],
            for i in range(0, ((40 * int(item[1])) / maxi)):
                sys.stdout.write('*')
            for i in range(((40 * int(item[1])) / maxi), 40):
                sys.stdout.write(' ')
            print ' %5s' % item[1]


def pretty_print(iden, action, keys, values):
    """
    Pretty print aggregation walker.
    """
    if action in [1799]:
        print keys, values
    elif action == 1800:
        # lquantize
        print '\n    ', keys[0], '\n'
        print '{0:>10s} {1:-^40} {2}'.format('value', ' Distribution ',
                                             'count')
        print_lquantize(values)
    else:
        pass


def brendan():
    """
    DTrace fans will understand this :-D
    """
    print 'Tracing... Hit Ctrl-C to end'


def run_dtrace(script):
    """
    Run DTrace till Ctrl+C is pressed...
    """
    thr = DTraceConsumerThread(script, False, walk_func=pretty_print)
    thr.start()
    brendan()
    try:
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        thr.stop()
        thr.join()

if __name__ == '__main__':
    # run_dtrace('dtrace:::BEGIN {trace("Hello World"); exit(0);}')
    # run_dtrace('syscall:::entry { @num[pid,execname] = count(); }')
    TMP = 'syscall::read:entry { @dist[execname] = lquantize(arg0, 0, 12, 2);}'
    run_dtrace(TMP)
    # run_dtrace('sysinfo:::readch { @dist[execname] = quantize(arg0); }')
