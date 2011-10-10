#!/usr/bin/env python

'''
Use the Python DTrace consumer and run a syscall counter DTrace script.

Created on Oct 10, 2011

@author: tmetsch
'''

from dtrace.consumer import DTraceConsumer

script = 'syscall:::entry { @num[execname] = count(); }'

def main():
    consumer = DTraceConsumer()
    consumer.run_script(script, 4)

if __name__ == '__main__':
    main()
