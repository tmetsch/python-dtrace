#!/usr/bin/env python

'''
Setup script.

Created on Oct 10, 2011

@author: tmetsch
'''

try:
    from Cython.Distutils import build_ext
except ImportError:
    print('Cython seems not to be present. You might still be able to use the \
           ctypes DTrace wrapper. Or install cython and try again.')
    exit(1)
from distutils.core import setup
from distutils.extension import Extension


setup(name='python-dtrace',
      version='0.0.2',
      description='DTrace consumer for Python based on libdtrace. Use Python \
                   now as DTrace Consumer and Provider!',
      license='TBD',
      keywords='DTrace',
      url='http://tmetsch.github.com/python-dtrace/',
      packages=['dtrace_ctypes'],
      cmdclass={'build_ext': build_ext},
      ext_modules=[Extension("dtrace", ["dtrace/dtrace.pyx",
                                        "dtrace/dtrace_h.pxd"],
                             libraries=["dtrace"])],
      classifiers=["Development Status :: 2 - Pre-Alpha",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python"
                   ],
     )
