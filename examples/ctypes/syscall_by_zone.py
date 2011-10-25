#!/usr/bin/env python

'''
Use the Python DTrace consumer and count syscalls by zone.

Created on Oct 10, 2011

@author: tmetsch
'''


from ctypes import cast, c_char_p, c_int
from dtrace_ctypes.consumer import DTraceConsumerThread, deref
import time

SCRIPT = 'syscall:::entry { @num[zonename] = count(); }'


def walk(data, arg):
    '''
    Nice formatted aggregate walker.
    '''
    tmp = data.contents.dtada_data

    name = cast(tmp + 16, c_char_p).value
    count = deref(tmp + 272, c_int).value

    print 'Zone "{0:s}" made {1:d} syscalls.'.format(name, count)

    return 0


def main():
    '''
    Run DTrace...
    '''
    dtrace = DTraceConsumerThread(SCRIPT, walk_func=walk)
    dtrace.start()

    # we will stop the thread after some time...
    time.sleep(5)

    # stop and wait for join...
    dtrace.stop()
    dtrace.join()

if __name__ == '__main__':
    main()
