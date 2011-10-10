#!/usr/bin/env python

'''
Use the Python DTrace consumer and run a Hello World DTrace script.

Created on Oct 10, 2011

@author: tmetsch
'''

from dtrace.consumer import DTraceConsumer

script = 'dtrace:::BEGIN {trace("Hello World");}'

def main():
    consumer = DTraceConsumer()
    consumer.run_script(script)

if __name__ == '__main__':
    main()
