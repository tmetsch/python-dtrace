
Python as a DTrace consumer
===========================

This is a first shot into looking at getting something up and running like
https://github.com/bcantrill/node-libdtrace for Python.

Note: This is far from ready - documentation on writing own DTrace consumers
is very rare :-

The codes in the **examples** folder should give an overview of how to use
Python as a DTrace consumer.

Currently this package provides two modules: one wraps libdtrace using ctypes.
The other one uses cython. Should you not have cython installed the ctypes
wrapper can still be used.

The Python DTrace consumer can be installed via source here on GitHub, or using
[pypi](http://pypi.python.org/pypi/python-dtrace "python-dtrace on pypi").

Cython based wrapper
--------------------

The Cython wrapper is more sophisticated and generally easier to use.
Initializing the Python based DTrace consumer is as simple as:

    from dtrace import DTraceConsumer
    consumer = DTraceConsumer(walk_func=my_walk [...])
    consumer.run_script(SCRIPT, runtime=3)

The simple DTraceConsumer can be initialized with self written callbacks which
will allow you to get the output from DTrace, the chewing of the probes as well
as walking the aggregate at the end of the DTrace run. The signatures looks
like this:

    def simple_chew(cpu):
        pass

    def simple_chewrec(action):
        pass

    def simple_out(value):
        pass

    def simple_walk(id, key, value):
        pass

Those functions can also be part of a class. Simply add the self parameter as
the first one:

    def simple_chew(self, cpu):
        pass

The DTraceConsumer has a run_script function which will run a provided DTrace
script for some time or till it is finished. The time on how long it is run can
be provided as parameter just like the script. During the DTrace chew, chewrec
and the out callbacks are called. When the run is finished the aggregation will
be walked.

There also exists and DTraceConsumerThread which can be used to continuously
run DTrace in the background. This might come in handy when you want to
continuously aggregate data for e.g. an GUI. The chew, chewrec, out and walk
callbacks are now called as the probes fire. The signatures and way of handling
are the same as for the DTraceConsumer:

    consumer = DTraceConsumerThread(SCRIPT, walk_func=my_walk [...])
    dtrace = Thread(target=consumer.run) # cython requires this :-/
    dtrace.start()

    # we will stop the thread after some time...
    time.sleep(2)

    # stop and wait for join...
    consumer.stop()
    dtrace.join()

Examples for both ways of handling the Python DTrace consumer can be found in
the *examples* folder.

Ctypes based wrapper
--------------------

Both the DTraceConsumer and the DTraceConsumerThread can be initialized with
self written chew, chewrec, buffered out and walk functions just like in the
cython approach. See the examples on how to do this. Also note that the out,
walk, chew and chewrec are currently limited in their functionality and require
you to understand how ctypes work. For examples on how to implement those
functions please review the consumer module in the dtrace_ctypes package. The
functions are named: **simple_chew**, **simple_chewrec**, **simple_walk** and
**simple_buffered_out_writer function**.

The examples for using this libdtrace wrapper can be found in the
*examples/ctypes* folder.

(c) 2011 Thijs Metsch
