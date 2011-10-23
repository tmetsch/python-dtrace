#!/usr/bin/env python

'''
Setup script.

Created on Oct 10, 2011

@author: tmetsch
'''

from distutils.core import setup
from distutils.extension import Extension
try:
    from Cython.Distutils import build_ext

    BUILD_EXTENSION = {'build_ext': build_ext}
    EXT_MODULES = [Extension("dtrace", ["dtrace/dtrace.pyx",
                                        "dtrace/dtrace_h.pxd"],
                             libraries=["dtrace"])]

except ImportError:
    BUILD_EXTENSION = {}
    EXT_MODULES = None
    print('Cython seems not to be present. Currently you will only be able '
          + 'to use the ctypes wrapper. Or you can install cython and try '
          + 'again.')


setup(name='python-dtrace',
      version='0.0.2',
      description='DTrace consumer for Python based on libdtrace. Use Python \
                   now as DTrace Consumer and Provider!',
      license='TBD',
      keywords='DTrace',
      url='http://tmetsch.github.com/python-dtrace/',
      packages=['dtrace', 'dtrace_ctypes'],
      cmdclass=BUILD_EXTENSION,
      ext_modules=EXT_MODULES,
      classifiers=["Development Status :: 2 - Pre-Alpha",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python"
                   ],
     )
