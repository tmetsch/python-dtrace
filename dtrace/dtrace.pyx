
import time

cdef extern from "libelf_workaround.h":
    # lib elf workaround :-/
    pass

cdef extern from "dtrace.h":
    # taken from /usr/include/dtrace.h
    ctypedef struct dtrace_hdl_t:
        pass

    ctypedef struct dtrace_bufdata_t:
        char *dtbda_buffered
        pass

    ctypedef struct dtrace_prog_t:
        pass

    ctypedef struct dtrace_proginfo_t:
        pass

    ctypedef enum dtrace_workstatus_t:
        DTRACE_WORKSTATUS_ERROR = -1,
        DTRACE_WORKSTATUS_OKAY,
        DTRACE_WORKSTATUS_DONE

    ctypedef struct dtrace_aggdata_t:
        pass

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

    ctypedef int dtrace_handle_buffered_f(dtrace_bufdata_t *buf_data, void *arg)
    ctypedef int dtrace_consume_probe_f(dtrace_probedata_t *, void *)
    ctypedef int dtrace_consume_rec_f(dtrace_probedata_t *, dtrace_recdesc_t *, void *)
    ctypedef int dtrace_aggregate_f(dtrace_aggdata_t *, void *)

    # open and close handle
    dtrace_hdl_t* dtrace_open(int, int, int *)
    void dtrace_close(dtrace_hdl_t *handle)

    # options
    int dtrace_setopt(dtrace_hdl_t *, char *, char *)

    # output handling
    int dtrace_handle_buffered(dtrace_hdl_t *, dtrace_handle_buffered_f *, void *)
    int dtrace_consume_probe_f(dtrace_probedata_t *, void *)
    int dtrace_consume_rec_f(dtrace_probedata_t *, dtrace_recdesc_t *, void *)
    int dtrace_aggregate_f(dtrace_aggdata_t *, void *)

    # compile
    dtrace_prog_t* dtrace_program_strcompile(dtrace_hdl_t *, char *, dtrace_probespec_t, int, int, char *const [])

    # running
    int dtrace_program_exec(dtrace_hdl_t *, dtrace_prog_t *, dtrace_proginfo_t *)
    int dtrace_go(dtrace_hdl_t *)
    int dtrace_stop(dtrace_hdl_t *)
    void dtrace_sleep(dtrace_hdl_t *)
    dtrace_workstatus_t dtrace_work(dtrace_hdl_t *, char *, dtrace_consume_probe_f *, dtrace_consume_rec_f *, void *)

    # walking aggregate
    int dtrace_aggregate_walk_valsorted(dtrace_hdl_t *, dtrace_aggregate_f *, void *)

    # error handling...
    int dtrace_errno(dtrace_hdl_t *handle)
    char *dtrace_errmsg(dtrace_hdl_t *handle, int error)

cdef int chew(dtrace_probedata_t *data, void *arg):
    return 0

cdef int chewrec(dtrace_probedata_t *data, dtrace_recdesc_t *rec, void *arg):
    return 0

cdef int buf_out(dtrace_bufdata_t *buf_data, void *arg):
    print(buf_data.dtbda_buffered.strip())
    return 0

cdef int walk(dtrace_aggdata_t *data, void *arg):
    return 0

cdef class DTraceConsumer:
    cdef dtrace_hdl_t *handle

    def __init__(self):
        '''
        Get a DTrace handle.
        '''
        self.handle = dtrace_open(3, 0, NULL)
        if self.handle == NULL:
            raise Exception(dtrace_errmsg(NULL, dtrace_errno(self.handle)))

        # set buffer options
        if dtrace_setopt(self.handle, 'bufsize', '4m') != 0:
            raise Exception(dtrace_errmsg(NULL, dtrace_errno(self.handle)))

        if dtrace_setopt(self.handle, 'aggsize', '4m') != 0:
            raise Exception(dtrace_errmsg(NULL, dtrace_errno(self.handle)))

    def __del__(self):
        '''
        Release DTrace handle.
        '''
        dtrace_close(self.handle)

    cpdef run_script(self, char *script, runtime=1):
        '''
        Run a DTrace script for a number of seconds defined by the runtime.

        After the run is complete the aggregate is walked. During execution the
        stdout of DTrace is redirected to the chew, chewrec and buffered output
        writer.

        script -- The script to run.
        runtime -- The time the script should run in second (Default: 1s).
        '''
        # set simple output callbacks
        if dtrace_handle_buffered(self.handle, &buf_out, NULL) == -1:
            raise Exception('Unable to set the stdout buffered writer.')

        # compile
        cdef dtrace_prog_t *prg
        prg = dtrace_program_strcompile(self.handle, script,
                                        DTRACE_PROBESPEC_NAME, 0, 0, NULL)
        if prg == NULL:
            raise Exception('Unable to compile the script: ',
                            dtrace_errmsg(NULL, dtrace_errno(self.handle)))

        # run
        if dtrace_program_exec(self.handle, prg, NULL) == -1:
            raise Exception('Failed to execute: ',
                            dtrace_errmsg(NULL, dtrace_errno(self.handle)))
        if dtrace_go(self.handle) != 0:
            raise Exception('Failed to run_script: ',
                            dtrace_errmsg(NULL, dtrace_errno(self.handle)))

        i = 0
        while i < runtime:
            dtrace_sleep(self.handle)
            dtrace_work(self.handle, NULL, &chew, &chewrec, NULL)

            time.sleep(1)
            i += 1

        dtrace_stop(self.handle)

        # sorting instead of dtrace_aggregate_walk
        if dtrace_aggregate_walk_valsorted(self.handle, &walk, NULL) != 0:
            raise Exception('Failed to walk the aggregate: ',
                            dtrace_errmsg(NULL, dtrace_errno(self.handle)))

        print 'here I am...'


