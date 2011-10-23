#!/usr/bin/env python2.7
'''
Created on Oct 21, 2011

@author: tmetsch
'''
from dtrace import DTraceConsumer

SCRIPT = 'dtrace:::BEGIN {trace("Hello World");}'


def main():
    '''
    Run Dtrace...
    '''
    consumer = DTraceConsumer()
    consumer.run_script(SCRIPT)

if __name__ == '__main__':
    main()
