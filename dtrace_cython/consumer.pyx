from __future__ import print_function, division
import time
import threading
from threading import Thread

from dtrace_cython.dtrace_h cimport *
from libc.stdint cimport INT64_MAX, INT64_MIN
from libc.stdio cimport fclose
from libc.stdlib cimport free
from posix.stdio cimport open_memstream

# ----------------------------------------------------------------------------
# The DTrace callbacks
# ----------------------------------------------------------------------------


cdef int chew(const dtrace_probedata_t * data, void * arg) with gil:
    """
    Callback defined by DTrace - will call the Python callback.

    Called once per fired probe...
    """

    tmp = <set>arg
    function = <object>tmp[0]

    cpu = data.dtpda_cpu

    function(cpu)

    return 0


cdef int chewrec(const dtrace_probedata_t * data, const dtrace_recdesc_t * rec,
                 void * arg) with gil:
    """
    Callback defined by DTrace - will call the Python callback.

    Called once per action.
    """

    if rec == NULL:
        return 0

    tmp = <set>arg
    function = <object>tmp[1]

    action = rec.dtrd_action
    function(action)

    return 0


cdef int buf_out(const dtrace_bufdata_t * buf_data, void * arg) with gil:
    """
    Callback defined by DTrace - will call the Python callback.
    """

    value = buf_data.dtbda_buffered.strip()

    function = <object>arg
    function(value)

    return 0


cdef int walk(const dtrace_aggdata_t * data, void * arg) with gil:
    """
    Callback defined by DTrace - will call the Python callback.
    """

    keys = []
    value = None

    desc = data.dtada_desc
    iden = desc.dtagd_varid
    cdef dtrace_recdesc_t *rec
    cdef int64_t *tmp

    aggrec = &desc.dtagd_rec[desc.dtagd_nrecs - 1]
    action = aggrec.dtrd_action

    for i in range(1, desc.dtagd_nrecs - 1):
        rec = &desc.dtagd_rec[i]
        address = data.dtada_data + rec.dtrd_offset

        # TODO: need to extend this.
        if rec.dtrd_size == sizeof(uint32_t):
            keys.append((<int32_t *>address)[0])
        else:
            keys.append(<char *>address)

    if action in [DTRACEAGG_SUM, DTRACEAGG_MAX, DTRACEAGG_MIN,
                  DTRACEAGG_COUNT]:
        value = (<int *>(data.dtada_data + aggrec.dtrd_offset))[0]
    elif action == DTRACEAGG_AVG:
        tmp = <int64_t *>(data.dtada_data + aggrec.dtrd_offset)
        value = tmp[1] // tmp[0]
    elif action == DTRACEAGG_QUANTIZE:
        tmp = <int64_t *>(data.dtada_data + aggrec.dtrd_offset)
        ranges = get_quantize_ranges()
        quantize = []
        for i in range(0, len(ranges)):
            quantize.append((ranges[i], tmp[i]))

        value = quantize
    elif action == DTRACEAGG_LQUANTIZE:
        tmp = <int64_t *>(data.dtada_data + aggrec.dtrd_offset)
        quantize = []
        tmp_arg = tmp[0]

        ranges = get_lquantize_ranges(tmp_arg)
        levels = (aggrec.dtrd_size // sizeof (uint64_t)) - 1
        for i in range(0, levels):
            # i + 1 since tmp[0] is already 'used'
            quantize.append((ranges[i], tmp[i + 1]))

        value = quantize
    else:
        raise Exception('Unsupported DTrace aggregation function!')

    function = <object>arg
    function(action, iden, keys, value)

    # DTRACE_AGGWALK_REMOVE
    return 5

# ----------------------------------------------------------------------------
# Helper functions for the walk...
# ----------------------------------------------------------------------------


cdef get_quantize_ranges():
    ranges = []

    for i in range(0, DTRACE_QUANTIZE_NBUCKETS):
        if i < DTRACE_QUANTIZE_ZEROBUCKET:
            if i > 0:
                mini = DTRACE_QUANTIZE_BUCKETVAL(i -1) + 1
            else:
                # INT64_MIN
                mini = INT64_MIN
            maxi = DTRACE_QUANTIZE_BUCKETVAL(i)
        elif i == DTRACE_QUANTIZE_ZEROBUCKET:
            mini = 0
            maxi = 0
        else:
            mini = DTRACE_QUANTIZE_BUCKETVAL(i)
            if i < DTRACE_QUANTIZE_NBUCKETS - 1:
                maxi = DTRACE_QUANTIZE_BUCKETVAL(i + 1) -1
            else:
                # INT64_MAX
                maxi = INT64_MAX
        ranges.append((mini, maxi))

    return ranges


cdef get_lquantize_ranges(uint64_t arg):
    ranges = []

    base = DTRACE_LQUANTIZE_BASE(arg)
    step = DTRACE_LQUANTIZE_STEP(arg)
    levels = DTRACE_LQUANTIZE_LEVELS(arg)

    for i in range(0, levels + 2):
        if i == 0:
            mini = INT64_MIN
        else:
            mini = base + ((i - 1) * step)
        if i > levels:
            maxi = INT64_MAX
        else:
            maxi = base + (i * step) - 1
        ranges.append((mini, maxi))

    return ranges

# ----------------------------------------------------------------------------
# Default Python callbacks
# ----------------------------------------------------------------------------


def simple_chew(cpu):
    """
    Simple chew function.

    cpu -- CPU id.
    """
    print('Running on CPU:', cpu)


def simple_chewrec(action):
    """
    Simple chewrec callback.

    action -- id of the action which was called.
    """
    print('Called action was:', action)


def simple_out(value):
    """
    A buffered output handler for all those prints.

    value -- Line by line string of the DTrace output.
    """
    print('Value is:', value)


def simple_walk(action, identifier, keys, value):
    """
    Simple aggregation walker.

    action -- the aggregation action.
    identifier -- the id.
    action -- type of action (sum, avg, ...)
    keys -- list of keys.
    value -- the value.
    """
    print(action, identifier, keys, value)

# ----------------------------------------------------------------------------
# The consumers
# ----------------------------------------------------------------------------

cdef int _dtrace_sleep_and_work(dtrace_hdl_t * handle, void * args, out_func):
    cdef FILE *fp = NULL
    IF UNAME_SYSNAME == "Darwin":
        cdef char *memstream
        cdef size_t size
        # Note: macOS crashes if we pass NULL for fp (FreeBSD works fine)
        # As a workaround we use open_memstream to write to memory.
        fp = open_memstream(&memstream, &size)
        assert fp != NULL
    status = dtrace_work(handle, fp, &chew, &chewrec, <void *> args)
    IF UNAME_SYSNAME == "Darwin":
        fclose(fp)
        out_func((<bytes> memstream).strip())
        free(memstream)
    if status == DTRACE_WORKSTATUS_ERROR:
        raise Exception('dtrace_work failed: ',
                        dtrace_errmsg(handle, dtrace_errno(handle)))
    return status


cdef class DTraceConsumer:
    """
    A Pyton based DTrace consumer.
    """

    cdef dtrace_hdl_t * handle
    cdef object out_func
    cdef object walk_func
    cdef object chew_func
    cdef object chewrec_func

    def __init__(self, chew_func=None, chewrec_func=None, out_func=None,
                 walk_func=None):
        """
        Constructor. Gets a DTrace handle and sets some options.
        """
        self.chew_func = chew_func or simple_chew
        self.chewrec_func = chewrec_func or simple_chewrec
        self.out_func = out_func or simple_out
        self.walk_func = walk_func or simple_walk

        cdef int err
        if not hasattr(self, 'handle'):
            # ensure we only grab 1 - cython might call init twice, of more.
            self.handle = dtrace_open(3, 0, &err)
        if self.handle == NULL:
            raise Exception(dtrace_errmsg(NULL, err))

        # set buffer options
        if dtrace_setopt(self.handle, 'bufsize', '4m') != 0:
            raise Exception(dtrace_errmsg(self.handle, 
                                          dtrace_errno(self.handle)))

        if dtrace_setopt(self.handle, 'aggsize', '4m') != 0:
            raise Exception(dtrace_errmsg(self.handle,
                                          dtrace_errno(self.handle)))

    def __dealloc__(self):
        """
        Release DTrace handle.
        """
        if hasattr(self, 'handle') and self.handle != NULL:
            dtrace_close(self.handle)

    cpdef compile(self, str script):
        """
        Compile a DTrace script and return errors if any.
        
        script -- The script to compile.
        """
        cdef dtrace_prog_t * prg
        prg = dtrace_program_strcompile(self.handle, script.encode("utf-8"),
                                        DTRACE_PROBESPEC_NAME, 0, 0, NULL)
        if prg == NULL:
            raise Exception('Unable to compile the script: ',
                            dtrace_errmsg(self.handle,
                                          dtrace_errno(self.handle)))

    cpdef run(self, str script, runtime=1):
        """
        Run a DTrace script for a number of seconds defined by the runtime.

        After the run is complete the aggregate is walked. During execution the
        stdout of DTrace is redirected to the chew, chewrec and buffered output
        writer.

        script -- The script to run.
        runtime -- The time the script should run in second (Default: 1s).
        """
        # set simple output callbacks
        if dtrace_handle_buffered(self.handle, & buf_out,
                                  <void *>self.out_func) == -1:
            raise Exception('Unable to set the stdout buffered writer.')

        # compile
        cdef dtrace_prog_t * prg
        prg = dtrace_program_strcompile(self.handle, script.encode("utf-8"),
                                        DTRACE_PROBESPEC_NAME, 0, 0, NULL)
        if prg == NULL:
            raise Exception('Unable to compile the script: ',
                            dtrace_errmsg(self.handle,
                                          dtrace_errno(self.handle)))

        # run
        if dtrace_program_exec(self.handle, prg, NULL) == -1:
            raise Exception('Failed to execute: ',
                            dtrace_errmsg(self.handle,
                                          dtrace_errno(self.handle)))
        if dtrace_go(self.handle) != 0:
            raise Exception('Failed to run_script: ',
                            dtrace_errmsg(self.handle,
                                          dtrace_errno(self.handle)))

        i = 0
        args = (self.chew_func, self.chewrec_func)
        while i < runtime:
            dtrace_sleep(self.handle)
            status = _dtrace_sleep_and_work(self.handle, <void *>args,
                                            self.out_func)
            if status == DTRACE_WORKSTATUS_DONE:
                break
            elif status == DTRACE_WORKSTATUS_ERROR:
                raise Exception('dtrace_work failed: ',
                                dtrace_errmsg(self.handle,
                                              dtrace_errno(self.handle)))
            else:
                assert status == DTRACE_WORKSTATUS_OKAY, status
                time.sleep(1)
                i += 1
                
        dtrace_stop(self.handle)

        # walk the aggregate
        # sorting instead of dtrace_aggregate_walk
        if dtrace_aggregate_walk_valsorted(self.handle, & walk,
                                           <void *>self.walk_func) != 0:
            raise Exception('Failed to walk the aggregate: ',
                            dtrace_errmsg(self.handle,
                                          dtrace_errno(self.handle)))


cdef class DTraceContinuousConsumer:
    """
    Continuously consuming DTrace consumer
    """

    cdef dtrace_hdl_t * handle
    cdef object out_func
    cdef object walk_func
    cdef object chew_func
    cdef object chewrec_func
    cdef object script

    def __init__(self, str script, chew_func=None, chewrec_func=None,
                 out_func=None, walk_func=None):
        """
        Constructor. will get the DTrace handle
        """
        self.chew_func = chew_func or simple_chew
        self.chewrec_func = chewrec_func or simple_chewrec
        self.out_func = out_func or simple_out
        self.walk_func = walk_func or simple_walk
        self.script = script.encode("utf-8")

        cdef int err
        if not hasattr(self, 'handle'):
            # ensure we only grab 1 - cython might call init twice, of more.
            self.handle = dtrace_open(3, 0, &err)
        if self.handle == NULL:
            raise Exception(dtrace_errmsg(NULL, err))

        # set buffer options
        if dtrace_setopt(self.handle, 'bufsize', '4m') != 0:
            raise Exception(dtrace_errmsg(self.handle,
                                          dtrace_errno(self.handle)))

        if dtrace_setopt(self.handle, 'aggsize', '4m') != 0:
            raise Exception(dtrace_errmsg(self.handle,
                                          dtrace_errno(self.handle)))

    def __dealloc__(self):
        """
        Release DTrace handle.
        """
        if hasattr(self, 'handle') and self.handle != NULL:
            dtrace_stop(self.handle)
            dtrace_close(self.handle)

    cpdef go(self):
        """
        Compile DTrace program.
        """
        # set simple output callbacks
        if dtrace_handle_buffered(self.handle, & buf_out,
                                  <void *>self.out_func) == -1:
            raise Exception('Unable to set the stdout buffered writer.')

        # compile
        cdef dtrace_prog_t * prg
        prg = dtrace_program_strcompile(self.handle, self.script,
                                        DTRACE_PROBESPEC_NAME, 0, 0, NULL)
        if prg == NULL:
            raise Exception('Unable to compile the script: ',
                            dtrace_errmsg(self.handle,
                                          dtrace_errno(self.handle)))

        # run
        if dtrace_program_exec(self.handle, prg, NULL) == -1:
            raise Exception('Failed to execute: ',
                            dtrace_errmsg(self.handle,
                      dtrace_errno(self.handle)))
        if dtrace_go(self.handle) != 0:
            raise Exception('Failed to run_script: ',
                            dtrace_errmsg(self.handle,
                                          dtrace_errno(self.handle)))

    def sleep(self):
        """
        Wait for new data to arrive.

        WARN: This method will acquire the Python GIL!
        """
        dtrace_sleep(self.handle)

    def snapshot(self):
        """
        Snapshot the data and walk the aggregate.
        """
        args = (self.chew_func, self.chewrec_func)
        status = _dtrace_sleep_and_work(self.handle, <void *>args,
                                        self.out_func)
        if dtrace_aggregate_snap(self.handle) != 0:
            raise Exception('Failed to get the aggregate: ',
                            dtrace_errmsg(self.handle,
                              dtrace_errno(self.handle)))
        if dtrace_aggregate_walk_valsorted(self.handle, & walk,
                                           <void *>self.walk_func) != 0:
            raise Exception('Failed to walk aggregate: ',
                            dtrace_errmsg(self.handle,
                                          dtrace_errno(self.handle)))

        return status


class DTraceConsumerThread(Thread):
    """
    Helper Thread which can be used to continuously aggregate.
    """

    def __init__(self, script, consume=True, chew_func=None, chewrec_func=None,
                 out_func=None, walk_func=None, sleep=0):
        """
        Initilizes the Thread.
        """
        Thread.__init__(self)
        self._should_stop = threading.Event()
        self.sleep_time = sleep
        self.consume = consume
        self.consumer = DTraceContinuousConsumer(script, chew_func,
                                                 chewrec_func, out_func,
                                                 walk_func)

    def __del__(self):
        """
        Make sure DTrace stops.
        """
        if not self.consume:
            self.consumer.snapshot()
        del self.consumer

    def run(self):
        """
        Aggregate data...
        """
        Thread.run(self)

        self.consumer.go()
        while not self.stopped():
            if self.sleep_time == 0:
                self.consumer.sleep()
            else:
                time.sleep(self.sleep_time)

            if self.consume:
                status = self.consumer.snapshot()
                if status == DTRACE_WORKSTATUS_DONE:
                    self.stop()

    def stop(self):
        """
        Stop DTrace.
        """
        self._should_stop.set()

    def stopped(self):
        """
        Used to check the status.
        """
        return self._should_stop.isSet()
