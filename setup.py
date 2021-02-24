#!/usr/bin/env python

"""
Setup script.

Created on Oct 10, 2011

@author: tmetsch
"""

from distutils.core import setup
from distutils.extension import Extension
import os
import platform
import sys
try:
    from Cython.Build import build_ext, cythonize
    extra_args = {}
    if platform.system().lower().startswith("freebsd"):
        # On older FreeBSD versions the dtrace headers are not
        # installed by default, so we need to find the full sources.
        if not os.path.exists("/usr/include/dtrace.h"):
            src_dir = os.getenv("FREEBSD_SRC_DIR", "/usr/src")
            if not os.path.exists(os.path.join(src_dir, "sys/cddl")):
                raise ImportError("Cannot find FreeBSD DTrace headers")
            extra_args["include_dirs"] = [
                os.path.join(src_dir,
                             "sys/cddl/compat/opensolaris"),
                os.path.join(src_dir,
                             "sys/cddl/contrib/opensolaris/uts/common"),
                os.path.join(src_dir,
                             "cddl/contrib/opensolaris/lib/libdtrace/common"),
            ]
    if os.getenv("ENABLE_ASAN", None) is not None:
        extra_args["extra_compile_args"] = ["-fsanitize=address"]
        extra_args["extra_link_args"] = ["-fsanitize=address"]
    BUILD_EXTENSION = {'build_ext': build_ext}
    EXT_MODULES = cythonize(
        [
            Extension("dtrace", ["dtrace_cython/dtrace_h.pxd",
                                 "dtrace_cython/consumer.pyx"],
                      libraries=["dtrace"],
                      **extra_args)
        ],
        language_level=sys.version_info.major
    )

except ImportError:
    BUILD_EXTENSION = {}
    EXT_MODULES = None
    print('WARNING: Cython seems not to be present. Currently you will only'
          ' be able to use the ctypes wrapper. Or you can install cython and'
          ' try again.')


setup(name='python-dtrace',
      version='0.0.12',
      description='DTrace consumer for Python based on libdtrace. Use Python'
                  ' as DTrace Consumer and Provider! See the homepage for'
                  ' more information.',
      license='MIT',
      keywords='DTrace',
      url='http://tmetsch.github.io/python-dtrace/',
      packages=['dtrace_ctypes'],
      cmdclass=BUILD_EXTENSION,
      ext_modules=EXT_MODULES,
      classifiers=["Development Status :: 2 - Pre-Alpha",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python"
                   ])
