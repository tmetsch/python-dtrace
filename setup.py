#!/usr/bin/env python

'''
Setup script.

Created on Oct 10, 2011

@author: tmetsch
'''

from distutils.core import setup

setup(name='python-dtrace',
      version='0.0.1',
      description='DTrace consumer for Python based on libdtrace and ctypes. \
                   Use Python now as DTrace Consumer and Provider!',
      license='TBD',
      keywords='DTrace',
      url='https://github.com/tmetsch/python-dtrace',
      packages=['dtrace'],
      classifiers=["Development Status :: 2 - Pre-Alpha",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python"
                   ],
     )
