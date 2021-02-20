#!/usr/bin/env python

"""
Use the Python DTrace consumer and use stack().
"""

import dtrace

SCRIPT = "profile-99 /arg0/ { @foo[stack()] = count();}"


def main():
    """
    Run DTrace...
    """
    print('Hint: if you don\'t get any output try running it with pfexec...')

    consumer = dtrace.DTraceConsumer()
    consumer.run(SCRIPT, 4)


if __name__ == '__main__':
    main()
