
Python as a DTrace consumer
===========================

This is a first shot into looking at getting something up and running like https://github.com/bcantrill/node-libdtrace for Python. 

Note: This is far from ready - documentation on writing own DTrace consumers is very rare :-) Therefore I started of with main.c which is a simple starting point to interface DTrace.

Current design ideas on how to progress include:

 * Call libdtrace using ctypes directly (Might be hard because of the callbacks during aggregation)
 * Writing a simple C interface which is more 'pythonic' which than can be used in Python (maybe the way to go - but requires some work)
 * maybe even SWIG :-/
