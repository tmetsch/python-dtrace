
from libc.stdint cimport uint16_t, int32_t, uint32_t, int64_t, uint64_t


cdef extern from "libelf_workaround.h":
    # lib elf workaround :-/
    pass


cdef extern from "sys/dtrace.h":
    uint64_t DTRACE_QUANTIZE_NBUCKETS
    uint64_t DTRACE_QUANTIZE_ZEROBUCKET

    int DTRACEACT_AGGREGATION
    int DTRACEAGG_COUNT
    int DTRACEAGG_MIN
    int DTRACEAGG_MAX
    int DTRACEAGG_AVG
    int DTRACEAGG_SUM
    int DTRACEAGG_STDDEV # (unsupported)
    int DTRACEAGG_QUANTIZE
    int DTRACEAGG_LQUANTIZE

    ctypedef struct dtrace_recdesc_t:
        # Taken from sys/dtrace.h:931
        uint16_t dtrd_action
        uint32_t dtrd_offset
        uint32_t dtrd_size

    ctypedef struct dtrace_aggdesc_t:
        # Taken from sys/dtrace.h:950
        int dtagd_nrecs
        int64_t dtagd_varid
        dtrace_recdesc_t dtagd_rec[1]

    cdef uint16_t DTRACE_LQUANTIZE_STEP(uint64_t x)
    cdef uint16_t DTRACE_LQUANTIZE_LEVELS(uint64_t x)
    cdef int32_t DTRACE_LQUANTIZE_BASE(uint64_t x)
    cdef int64_t DTRACE_QUANTIZE_BUCKETVAL(uint64_t buck)


cdef extern from "dtrace.h":

    ctypedef enum dtrace_probespec_t:
        # Taken from dtrace.h:186
        DTRACE_PROBESPEC_NONE
        DTRACE_PROBESPEC_PROVIDER
        DTRACE_PROBESPEC_MOD
        DTRACE_PROBESPEC_FUNC
        DTRACE_PROBESPEC_NAME

    ctypedef enum dtrace_workstatus_t:
        # Taken from dtrace.h:247
        DTRACE_WORKSTATUS_ERROR
        DTRACE_WORKSTATUS_OKAY
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

    ctypedef struct dtrace_probedesc_t:
        uint32_t id
        char dtpd_provider[64]  # DTRACE_PROVNAMELEN
        char dtpd_mod[64]  # DTRACE_MODNAMELEN
        char dtpd_func[192]  # DTRACE_FUNCNAMELEN
        char dtpd_name[64]  # DTRACE_NAMELEN

    ctypedef struct dtrace_probedata_t:
        # Taken from dtrace.h:186
        dtrace_hdl_t * dtbda_handle
        dtrace_probedesc_t * dtpda_pdesc
        int dtpda_cpu

    ctypedef struct dtrace_bufdata_t:
        # Taken from dtrace.h:310
        dtrace_hdl_t * dtbda_handle
        const char * dtbda_buffered
        dtrace_probedata_t * dtbda_probe

    ctypedef struct dtrace_aggdata_t:
        # Taken from dtrace.h:351
        dtrace_aggdesc_t * dtada_desc
        char * dtada_data

    # from dtrace.h
    ctypedef int dtrace_handle_buffered_f(const dtrace_bufdata_t * buf_data, void * arg)
    ctypedef int dtrace_consume_probe_f(const dtrace_probedata_t *, void *)
    ctypedef int dtrace_consume_rec_f(const dtrace_probedata_t *, const dtrace_recdesc_t * , void *)
    ctypedef int dtrace_aggregate_f(const dtrace_aggdata_t *, void *)

    # open and close handle
    dtrace_hdl_t * dtrace_open(int, int, int *)
    void dtrace_close(dtrace_hdl_t * handle)

    # options
    int dtrace_setopt(dtrace_hdl_t * , char * , char *)

    # output handling
    int dtrace_handle_buffered(dtrace_hdl_t * , dtrace_handle_buffered_f * , void *)
    int dtrace_consume_probe_f(const dtrace_probedata_t * , void *)
    int dtrace_consume_rec_f(const dtrace_probedata_t * , dtrace_recdesc_t * , void *)
    int dtrace_aggregate_f(const dtrace_aggdata_t * , void *)

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
