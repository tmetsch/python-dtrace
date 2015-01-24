"""
The implementation of the consumer.

Created on Oct 10, 2011

@author: tmetsch
"""

from ctypes import cdll, CDLL, byref, c_int, c_char_p, CFUNCTYPE, c_void_p, \
    POINTER, cast
from dtrace_ctypes.dtrace_structs import dtrace_bufdata, dtrace_probedata, \
    dtrace_aggdata, dtrace_recdesc
from threading import Thread
import threading
import time

cdll.LoadLibrary("libdtrace.so")

LIBRARY = CDLL("libdtrace.so")

# =============================================================================
# chewing and output walkers
# =============================================================================


CHEW_FUNC = CFUNCTYPE(c_int,
                      POINTER(dtrace_probedata),
                      POINTER(c_void_p))
CHEWREC_FUNC = CFUNCTYPE(c_int,
                         POINTER(dtrace_probedata),
                         POINTER(dtrace_recdesc),
                         POINTER(c_void_p))
BUFFERED_FUNC = CFUNCTYPE(c_int,
                          POINTER(dtrace_bufdata),
                          POINTER(c_void_p))
WALK_FUNC = CFUNCTYPE(c_int,
                      POINTER(dtrace_aggdata),
                      POINTER(c_void_p))


def simple_chew_func(data, arg):
    """
    Callback for chew.
    """
    print 'CPU :', c_int(data.contents.dtpda_cpu).value
    return 0


def simple_chewrec_func(data, rec, arg):
    """
    Callback for record chewing.
    """
    if rec is None:
        return 1
    return 0


def simple_buffered_out_writer(bufdata, arg):
    """
    In case dtrace_work is given None as filename - this one is called.
    """
    tmp = c_char_p(bufdata.contents.dtbda_buffered).value.strip()
    print 'out >', tmp
    return 0


def simple_walk(data, arg):
    """
    Aggregate walker capable of reading a name and one value.
    """
    # TODO: pickup the 16 and 272 from offset in desc...

    tmp = data.contents.dtada_data
    name = cast(tmp + 16, c_char_p).value
    instance = deref(tmp + 272, c_int).value

    print '{0:60s} :{1:10d}'.format(name, instance)

    return 0

# =============================================================================
# Convenience stuff
# =============================================================================


def deref(addr, typ):
    """
    Deref a pointer.
    """
    return cast(addr, POINTER(typ)).contents


def get_error_msg(handle):
    """
    Get the latest and greatest DTrace error.
    """
    txt = LIBRARY.dtrace_errmsg(handle, LIBRARY.dtrace_errno(handle))
    return c_char_p(txt).value

# =============================================================================
# Consumers
# =============================================================================


class DTraceConsumer(object):
    """
    A Pyton based DTrace consumer.
    """

    def __init__(self,
                 chew_func=None,
                 chew_rec_func=None,
                 walk_func=None,
                 out_func=None):
        """
        Constructor. will get the DTrace handle
        """
        if chew_func is not None:
            self.chew = CHEW_FUNC(chew_func)
        else:
            self.chew = CHEW_FUNC(simple_chew_func)

        if chew_rec_func is not None:
            self.chew_rec = CHEWREC_FUNC(chew_rec_func)
        else:
            self.chew_rec = CHEWREC_FUNC(simple_chewrec_func)

        if walk_func is not None:
            self.walk = WALK_FUNC(walk_func)
        else:
            self.walk = WALK_FUNC(simple_walk)

        if out_func is not None:
            self.buf_out = BUFFERED_FUNC(out_func)
        else:
            self.buf_out = BUFFERED_FUNC(simple_buffered_out_writer)

        # get dtrace handle
        self.handle = LIBRARY.dtrace_open(3, 0, byref(c_int(0)))
        if self.handle is None:
            raise Exception('Unable to get a DTrace handle.')

        # set buffer options
        if LIBRARY.dtrace_setopt(self.handle, 'bufsize', '4m') != 0:
            raise Exception(get_error_msg(self.handle))

        if LIBRARY.dtrace_setopt(self.handle, 'aggsize', '4m') != 0:
            raise Exception(get_error_msg(self.handle))

    def __del__(self):
        """
        Always close the DTrace handle :-)
        """
        LIBRARY.dtrace_close(self.handle)

    def run_script(self, script, runtime=1):
        """
        Run a DTrace script for a number of seconds defined by the runtime.

        After the run is complete the aggregate is walked. During execution the
        stdout of DTrace is redirected to the chew, chewrec and buffered output
        writer.

        script -- The script to run.
        runtime -- The time the script should run in second (Default: 1s).
        """
        # set simple output callbacks
        if LIBRARY.dtrace_handle_buffered(self.handle, self.buf_out,
                                          None) == -1:
            raise Exception('Unable to set the stdout buffered writer.')

        # compile
        prg = LIBRARY.dtrace_program_strcompile(self.handle,
                                                script, 3, 4, 0, None)
        if prg is None:
            raise Exception('Unable to compile the script: ',
                            get_error_msg(self.handle))

        # run
        if LIBRARY.dtrace_program_exec(self.handle, prg, None) == -1:
            raise Exception('Failed to execute: ',
                            get_error_msg(self.handle))
        if LIBRARY.dtrace_go(self.handle) != 0:
            raise Exception('Failed to run_script: ',
                            get_error_msg(self.handle))

        # aggregate data for a few sec...
        i = 0
        while i < runtime:
            LIBRARY.dtrace_sleep(self.handle)
            LIBRARY.dtrace_work(self.handle, None, self.chew, self.chew_rec,
                                None)

            time.sleep(1)
            i += 1

        LIBRARY.dtrace_stop(self.handle)

        # sorting instead of dtrace_aggregate_walk

        #if dtrace_aggregate_walk_valsorted(self.handle,
        #                                   & walk,
        #                                   <void *>self.walk_func) != 0:
        import ctypes
        print LIBRARY.dtrace_aggregate_walk_valsorted(self.handle, self.walk, None)
        #if LIBRARY.dtrace_aggregate_walk_valsorted(self.handle,
        #                                           self.walk,
        #                                           c_void_p()) != 0:
        #    raise Exception('Failed to walk the aggregate: ',
        #                    get_error_msg(self.handle))


class DTraceConsumerThread(Thread):
    """
    Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition.
    """

    def __init__(self,
                 script,
                 chew_func=None,
                 chew_rec_func=None,
                 walk_func=None,
                 out_func=None):
        """
        Constructor. will get the DTrace handle
        """
        super(DTraceConsumerThread, self).__init__()
        self._stop = threading.Event()
        self.script = script

        if chew_func is not None:
            self.chew = CHEW_FUNC(chew_func)
        else:
            self.chew = CHEW_FUNC(simple_chew_func)

        if chew_rec_func is not None:
            self.chew_rec = CHEWREC_FUNC(chew_rec_func)
        else:
            self.chew_rec = CHEWREC_FUNC(simple_chewrec_func)

        if walk_func is not None:
            self.walk = WALK_FUNC(walk_func)
        else:
            self.walk = WALK_FUNC(simple_walk)

        if out_func is not None:
            self.buf_out = BUFFERED_FUNC(out_func)
        else:
            self.buf_out = BUFFERED_FUNC(simple_buffered_out_writer)

        # get dtrace handle
        self.handle = LIBRARY.dtrace_open(3, 0, byref(c_int(0)))
        if self.handle is None:
            raise Exception('Unable to get a DTrace handle.')

        # set buffer options
        if LIBRARY.dtrace_setopt(self.handle, 'bufsize', '4m') != 0:
            raise Exception(get_error_msg(self.handle))

        if LIBRARY.dtrace_setopt(self.handle, 'aggsize', '4m') != 0:
            raise Exception(get_error_msg(self.handle))

    def run(self):
        Thread.run(self)
        # set simple output callbacks
        if LIBRARY.dtrace_handle_buffered(self.handle, self.buf_out,
                                          None) == -1:
            raise Exception('Unable to set the stdout buffered writer.')

        # compile
        prg = LIBRARY.dtrace_program_strcompile(self.handle,
                                                self.script, 3, 4, 0,
                                                None)
        if prg is None:
            raise Exception('Unable to compile the script: ',
                            get_error_msg(self.handle))

        # run
        if LIBRARY.dtrace_program_exec(self.handle, prg, None) == -1:
            raise Exception('Failed to execute: ',
                            get_error_msg(self.handle))
        if LIBRARY.dtrace_go(self.handle) != 0:
            raise Exception('Failed to run_script: ',
                            get_error_msg(self.handle))

        # aggregate data for a few sec...
        while not self.stopped():
            LIBRARY.dtrace_sleep(self.handle)
            LIBRARY.dtrace_work(self.handle, None, self.chew, self.chew_rec,
                                None)

            if LIBRARY.dtrace_aggregate_snap(self.handle) != 0:
                raise Exception('Failed to snapshot the aggregate: ',
                                get_error_msg(self.handle))
            if LIBRARY.dtrace_aggregate_walk(self.handle, self.walk,
                                             None) != 0:
                raise Exception('Failed to walk the aggregate: ',
                                get_error_msg(self.handle))

        LIBRARY.dtrace_stop(self.handle)

    def stop(self):
        """
        Stop DTrace.
        """
        self._stop.set()

    def stopped(self):
        """
        Used to check the status.
        """
        return self._stop.isSet()
