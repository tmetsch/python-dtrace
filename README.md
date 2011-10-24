
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

There also exists and DTraceContinuousConsumer which can be used to
continuously run DTrace in the background. It can be embedded in a Thread as
showed below. This might come in handy when you want to continuously aggregate
data for e.g. an GUI. The chew, chewrec, out and walk callbacks are now called
as the snapshot function is called. In the while loop you can either wait for
new DTrace data to appear using *sleep* or just wait for some time. The
signatures for the callbacks are the same as for the DTraceConsumer:

    class MyThread(Thread):

        def __init__(self, script):
            Thread.__init__(self)
            self._stop = threading.Event()
            self.consumer = DTraceContinuousConsumer(script)

        def __del__(self):
            del(self.consumer)

        def run(self):
            Thread.run(self)

            while not self.stopped():
                time.sleep(1) # self.consumer.sleep()
                self.consumer.snapshot()

        def stop(self):
            '''
            Stop DTrace.
            '''
            self._stop.set()

        def stopped(self):
            '''
            Used to check the status.
            '''
            return self._stop.isSet()

Note that when using the *sleep* function the GIL from Python is acquired and
all your other code will not continue to run. Still it depends on what your
DTrace script does and how frequent you set it to fire the probes. Sometimes
the sleep does make sense. See the examples folder for more details.

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

Also note that I am looking into switching to cython to see if the callback
functions can be handled in a nicer way. Please see the cython-approach
branch.

(c) 2011 Thijs Metsch
