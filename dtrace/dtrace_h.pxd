
from libc.stdint cimport uint16_t, int32_t, uint32_t, int64_t, uint64_t

#from libc.stdint cimport *

cdef extern from "libelf_workaround.h":
    # lib elf workaround :-/
    pass


IF UNAME_SYSNAME == "Darwin":
    cdef extern from "stdint.h":
        # needed for quantize mths.
        cdef int64_t INT64_MAX
        cdef int64_t INT64_MIN
ELSE:
    cdef extern from "sys/int_limits.h":
        # needed for quantize mths.
        cdef int64_t INT64_MAX
        cdef int64_t INT64_MIN


cdef extern from "sys/dtrace.h":

    ctypedef enum agg_actions:
        # Taken from sys/dtrace.h:454
        # Needs to be in enum because ctypes wants it that way :-/
        DTRACEACT_AGGREGATION = 0x0700
        DTRACEAGG_COUNT = (DTRACEACT_AGGREGATION + 1)
        DTRACEAGG_MIN = (DTRACEACT_AGGREGATION + 2)
        DTRACEAGG_MAX = (DTRACEACT_AGGREGATION + 3)
        DTRACEAGG_AVG = (DTRACEACT_AGGREGATION + 4)
        DTRACEAGG_SUM = (DTRACEACT_AGGREGATION + 5)
        # + 6 is DTRACEAGG_STDDEV (unsupported)
        DTRACEAGG_QUANTIZE = (DTRACEACT_AGGREGATION + 7)
        DTRACEAGG_LQUANTIZE = (DTRACEACT_AGGREGATION + 8)

    ctypedef enum quantize_types:
        # NBBY = 8
        DTRACE_QUANTIZE_NBUCKETS = (((sizeof (uint64_t) * 8) - 1) * 2 + 1)
        DTRACE_QUANTIZE_ZEROBUCKET = ((sizeof (uint64_t) * 8) - 1)

    ctypedef struct dtrace_recdesc_t:
        # Taken from sys/dtrace.h:931
        int dtrd_action
        int dtrd_offset
        int dtrd_size

    ctypedef struct dtrace_aggdesc_t:
        # Taken from sys/dtrace.h:950
        int dtagd_nrecs
        int dtagd_varid
        dtrace_recdesc_t dtagd_rec[1]

    cdef uint16_t DTRACE_LQUANTIZE_STEP(long x)
    cdef uint16_t DTRACE_LQUANTIZE_LEVELS(long x)
    cdef int32_t DTRACE_LQUANTIZE_BASE(long x)
    cdef int64_t DTRACE_QUANTIZE_BUCKETVAL(long buck)

cdef extern from "dtrace.h":

    ctypedef enum dtrace_probespec_t:
        # Taken from dtrace.h:186
        DTRACE_PROBESPEC_NONE = -1
        DTRACE_PROBESPEC_PROVIDER = 0
        DTRACE_PROBESPEC_MOD
        DTRACE_PROBESPEC_FUNC
        DTRACE_PROBESPEC_NAME

    ctypedef enum dtrace_workstatus_t:
        # Taken from dtrace.h:247
        DTRACE_WORKSTATUS_ERROR = -1,
        DTRACE_WORKSTATUS_OKAY,
        DTRACE_WORKSTATUS_DONE

    ctypedef struct dtrace_hdl_t:
        # Taken from dtrace.h:54
        pass

    ctypedef struct dtrace_prog_t:
        # Taken from dtrace.h:58
        pass

    ctypedef struct dtrace_proginfo_t:
        # Taken from dtrace.h:97
        pass

    ctypedef struct dtrace_probedata_t:
        # Taken from dtrace.h:186
        int dtpda_cpu

    ctypedef struct dtrace_bufdata_t:
        # Taken from dtrace.h:310
        char * dtbda_buffered

    ctypedef struct dtrace_aggdata_t:
        # Taken from dtrace.h:351
        dtrace_aggdesc_t * dtada_desc
        char * dtada_data

    # from dtrace.h
    ctypedef int dtrace_handle_buffered_f(dtrace_bufdata_t * buf_data, void * arg)
    ctypedef int dtrace_consume_probe_f(dtrace_probedata_t * , void *)
    ctypedef int dtrace_consume_rec_f(dtrace_probedata_t * , dtrace_recdesc_t * , void *)
    ctypedef int dtrace_aggregate_f(dtrace_aggdata_t * , void *)

    # open and close handle
    dtrace_hdl_t * dtrace_open(int, int, int *)
    void dtrace_close(dtrace_hdl_t * handle)

    # options
    int dtrace_setopt(dtrace_hdl_t * , char * , char *)

    # output handling
    int dtrace_handle_buffered(dtrace_hdl_t * , dtrace_handle_buffered_f * , void *)
    int dtrace_consume_probe_f(dtrace_probedata_t * , void *)
    int dtrace_consume_rec_f(dtrace_probedata_t * , dtrace_recdesc_t * , void *)
    int dtrace_aggregate_f(dtrace_aggdata_t * , void *)

    # compile
    dtrace_prog_t * dtrace_program_strcompile(dtrace_hdl_t * , char * , dtrace_probespec_t, int, int, char * const [])

    # running
    int dtrace_program_exec(dtrace_hdl_t * , dtrace_prog_t * , dtrace_proginfo_t *)
    int dtrace_go(dtrace_hdl_t *)
    int dtrace_stop(dtrace_hdl_t *)
    void dtrace_sleep(dtrace_hdl_t *)
    dtrace_workstatus_t dtrace_work(dtrace_hdl_t * , char * , dtrace_consume_probe_f * , dtrace_consume_rec_f * , void *)

    # walking aggregate
    int dtrace_aggregate_walk_valsorted(dtrace_hdl_t * , dtrace_aggregate_f * , void *)
    int dtrace_aggregate_snap(dtrace_hdl_t *)
    int dtrace_aggregate_walk(dtrace_hdl_t *, dtrace_aggregate_f *, void *)

    # error handling...
    int dtrace_errno(dtrace_hdl_t * handle)
    char * dtrace_errmsg(dtrace_hdl_t * handle, int error)
