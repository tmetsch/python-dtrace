"""
The implementation of the consumer.

Created on Oct 10, 2011

@author: tmetsch
"""
from __future__ import print_function
import platform
import threading
import time
from ctypes import (byref, c_char_p, c_int, c_uint, c_void_p, cast, cdll,
                    CFUNCTYPE, POINTER)
from threading import Thread

from dtrace_ctypes.dtrace_structs import (dtrace_aggdata, dtrace_bufdata,
                                          dtrace_hdl_t, dtrace_probedata,
                                          dtrace_prog_t, dtrace_recdesc)

if platform.system().startswith("Darwin"):
    _LIBNAME = "libdtrace.dylib"
else:
    _LIBNAME = "libdtrace.so"
_LIBRARY = cdll.LoadLibrary(_LIBNAME)

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
    print('CPU :', c_int(data.contents.dtpda_cpu).value)
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
    print('out >', tmp)
    return 0


def simple_walk(data, arg):
    """
    Aggregate walker capable of reading a name and one value.
    """
    # TODO: pickup the 16 and 272 from offset in desc...

    tmp = data.contents.dtada_data
    name = cast(tmp + 16, c_char_p).value
    instance = deref(tmp + 272, c_int).value

    print('{0:60s} :{1:10d}'.format(name, instance))

    return 0

# =============================================================================
# LibDTrace function wrapper class
# =============================================================================


def _get_dtrace_fn(name, restype, argtypes):
    fn = getattr(_LIBRARY, name)
    fn.restype = restype
    fn.argtypes = argtypes
    return fn


class LIBRARY(object):
    # Types
    dtrace_proginfo_t = c_void_p
    dtrace_probespec_t = c_int  # actually an enum
    dtrace_workstatus_t = c_int  # actually an enum
    FILE_p = c_void_p  # FILE*
    # Functions
    dtrace_open = _get_dtrace_fn(
        "dtrace_open", dtrace_hdl_t, [c_int, c_int, POINTER(c_int)])
    dtrace_close = _get_dtrace_fn(
        "dtrace_close", None, [dtrace_hdl_t])
    dtrace_go = _get_dtrace_fn("dtrace_go", c_int, [dtrace_hdl_t])
    dtrace_stop = _get_dtrace_fn("dtrace_stop", c_int, [dtrace_hdl_t])
    dtrace_sleep = _get_dtrace_fn("dtrace_sleep", None, [dtrace_hdl_t])
    dtrace_work = _get_dtrace_fn(
        "dtrace_work", dtrace_workstatus_t,
        [dtrace_hdl_t, FILE_p, CHEW_FUNC, CHEWREC_FUNC, c_void_p])
    dtrace_errno = _get_dtrace_fn(
        "dtrace_errno", c_int, [dtrace_hdl_t])
    dtrace_errmsg = _get_dtrace_fn(
        "dtrace_errmsg", c_char_p, [dtrace_hdl_t, c_int])
    dtrace_setopt = _get_dtrace_fn(
        "dtrace_setopt", c_int, [dtrace_hdl_t, c_char_p, c_char_p])
    dtrace_handle_buffered = _get_dtrace_fn(
        "dtrace_handle_buffered", c_int,
        [dtrace_hdl_t, BUFFERED_FUNC, c_void_p])
    dtrace_aggregate_walk = _get_dtrace_fn(
        "dtrace_aggregate_walk", c_int,
        [dtrace_hdl_t, WALK_FUNC, c_void_p])
    dtrace_aggregate_walk_valsorted = _get_dtrace_fn(
        "dtrace_aggregate_walk_valsorted", c_int,
        [dtrace_hdl_t, WALK_FUNC, c_void_p])
    dtrace_aggregate_snap = _get_dtrace_fn(
        "dtrace_aggregate_snap", c_int, [dtrace_hdl_t])
    dtrace_program_strcompile = _get_dtrace_fn(
        "dtrace_program_strcompile", dtrace_prog_t,
        [dtrace_hdl_t, c_char_p, dtrace_probespec_t, c_uint, c_int,
         POINTER(c_char_p)])
    dtrace_program_exec = _get_dtrace_fn(
        "dtrace_program_exec", c_int,
        [dtrace_hdl_t, dtrace_prog_t, dtrace_proginfo_t])


# =============================================================================
# Convenience stuff
# =============================================================================


def deref(addr, typ):
    """
    Deref a pointer.
    """
    return cast(addr, POINTER(typ)).contents


def get_error_msg(handle, err=None):
    """
    Get the latest and greatest DTrace error.
    """
    if err is None:
        err = LIBRARY.dtrace_errno(handle)
    txt = LIBRARY.dtrace_errmsg(handle, err)
    return c_char_p(txt).value.decode("utf-8")

# =============================================================================
# Consumers
# =============================================================================

def _dtrace_open():
    err = c_int(0)
    handle = LIBRARY.dtrace_open(3, 0, byref(err))
    if handle is None or handle == 0:
        raise Exception('Unable to get a DTrace handle. Error=' +
                        get_error_msg(handle, err))
    assert isinstance(handle, dtrace_hdl_t)
    # set buffer options
    if LIBRARY.dtrace_setopt(handle, b'bufsize', b'4m') != 0:
        raise Exception(get_error_msg(handle))

    if LIBRARY.dtrace_setopt(handle, b'aggsize', b'4m') != 0:
        raise Exception(get_error_msg(handle))
    return handle


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
        self.handle = _dtrace_open()

    def __del__(self):
        """
        Always close the DTrace handle :-)
        """
        if hasattr(self, "handle"):  # Don't close if __init__ failed.
            LIBRARY.dtrace_close(self.handle)

    def run(self, script, runtime=1):
        """
        Run a DTrace script for a number of seconds defined by the runtime.

        After the run is complete the aggregate is walked. During execution the
        stdout of DTrace is redirected to the chew, chewrec and buffered output
        writer.

        script -- The script to run.
        runtime -- The time the script should run in second (Default: 1s).
        """
        # set simple output callbacks
        assert self.handle is not None
        if LIBRARY.dtrace_handle_buffered(self.handle, self.buf_out,
                                          None) == -1:
            raise Exception('Unable to set the stdout buffered writer.')

        # compile
        prg = LIBRARY.dtrace_program_strcompile(
            self.handle, c_char_p(script.encode("utf-8")), 3, 4, 0, None)
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

        if LIBRARY.dtrace_aggregate_walk_valsorted(self.handle, self.walk,
                                                   None) != 0:
            raise Exception('Failed to walk the aggregate: ',
                            get_error_msg(self.handle))


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
        self.handle = _dtrace_open()

    def __del__(self):
        """
        Always close the DTrace handle :-)
        """
        if hasattr(self, "handle"):  # Don't close if __init__ failed.
            LIBRARY.dtrace_close(self.handle)

    def run(self):
        Thread.run(self)
        assert self.handle is not None
        # set simple output callbacks
        if LIBRARY.dtrace_handle_buffered(self.handle, self.buf_out,
                                          None) == -1:
            raise Exception('Unable to set the stdout buffered writer.')

        # compile
        prg = LIBRARY.dtrace_program_strcompile(
            self.handle, c_char_p(self.script.encode("utf-8")), 3, 4, 0,
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
