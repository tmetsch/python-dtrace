
cdef extern from "libelf_workaround.h":
    # lib elf workaround :-/
    pass

cdef extern from "dtrace.h":
    # taken from /usr/include/dtrace.h

    ctypedef enum agg_types:
        DTRACEACT_AGGREGATION = 0x0700
        DTRACEAGG_COUNT = (DTRACEACT_AGGREGATION + 1)
        DTRACEAGG_MIN = (DTRACEACT_AGGREGATION + 2)
        DTRACEAGG_MAX = (DTRACEACT_AGGREGATION + 3)
        DTRACEAGG_SUM = (DTRACEACT_AGGREGATION + 5)

    ctypedef struct dtrace_hdl_t:
        pass

    ctypedef struct dtrace_bufdata_t:
        char * dtbda_buffered

    ctypedef struct dtrace_prog_t:
        pass

    ctypedef struct dtrace_proginfo_t:
        pass

    ctypedef enum dtrace_workstatus_t:
        DTRACE_WORKSTATUS_ERROR = -1,
        DTRACE_WORKSTATUS_OKAY,
        DTRACE_WORKSTATUS_DONE

    ctypedef struct dtrace_recdesc_t:
        int dtrd_action
        int dtrd_offset

    ctypedef struct dtrace_aggdesc_t:
        int dtagd_nrecs
        int dtagd_varid
        dtrace_recdesc_t dtagd_rec[1]

    ctypedef struct dtrace_aggdata_t:
        dtrace_aggdesc_t * dtada_desc
        char * dtada_data

    ctypedef struct dtrace_probedata_t:
        pass

    # taken from /usr/include/sys/dtrace.h
    ctypedef enum dtrace_probespec_t:
        DTRACE_PROBESPEC_NONE = -1
        DTRACE_PROBESPEC_PROVIDER = 0
        DTRACE_PROBESPEC_MOD
        DTRACE_PROBESPEC_FUNC
        DTRACE_PROBESPEC_NAME

    ctypedef struct dtrace_recdesc_t:
        pass

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

    # error handling...
    int dtrace_errno(dtrace_hdl_t * handle)
    char * dtrace_errmsg(dtrace_hdl_t * handle, int error)

    # python callbacks...
    void out_callback(char * val)
