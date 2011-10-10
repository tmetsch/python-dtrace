
Python as a DTrace consumer
===========================

This is a first shot into looking at getting something up and running like
https://github.com/bcantrill/node-libdtrace for Python.

Note: This is far from ready - documentation on writing own DTrace consumers
is very rare :-)

The codes in the examples folder should give an overview of how to use Python
as a DTrace consumer.

Bot the DTraceConsumer and the DTraceConsumerThread can be initialized with
self written chew, chewrec, buffered out and walk functions. See the examples
on how to do this - and see the simple implementations of those functions in
the consumers module.

(c) 2011 Thijs Metsch
