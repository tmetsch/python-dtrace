
import time
from dtrace.dtrace_h cimport *

cdef int chew(dtrace_probedata_t * data, void * arg) with gil:
    return 0

cdef int chewrec(dtrace_probedata_t * data, dtrace_recdesc_t * rec, void * arg) with gil:
    return 0

cdef int buf_out(dtrace_bufdata_t * buf_data, void * arg) with gil:

    value = buf_data.dtbda_buffered.strip()

    function = <object>arg
    function(value)

    return 0

cdef int walk(dtrace_aggdata_t * data, void * arg) with gil:

    key = []
    value = None

    desc = data.dtada_desc
    id = desc.dtagd_varid
    cdef dtrace_recdesc_t *rec

    aggrec = &desc.dtagd_rec[desc.dtagd_nrecs - 1]
    action = aggrec.dtrd_action

    for i in range(1, desc.dtagd_nrecs - 1):
            rec = &desc.dtagd_rec[i]
            address = data.dtada_data + rec.dtrd_offset
            key.append(<char *>address)

    if aggrec.dtrd_action in [DTRACEAGG_SUM,DTRACEAGG_MAX,DTRACEAGG_MIN,DTRACEAGG_COUNT]:
        value = (<int *>(data.dtada_data + aggrec.dtrd_offset))[0]
    else:
        print 'unsupported aggregating action!'

    function = <object>arg
    function(id, key, value)

    return 0

cdef class DTraceConsumer:

    cdef dtrace_hdl_t * handle
    cdef object out_func
    cdef object walk_func

    def __init__(self, out_func=None, walk_func=None):
        '''
        Get a DTrace handle.
        '''
        if out_func == None:
            self.out_func = self.simple_out
        else:
            self.out_func = out_func

        if walk_func == None:
            self.walk_func = self.simple_walk
        else:
            self.walk_func = walk_func

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

    cpdef simple_out(self, value):
        print value

    cpdef simple_walk(self, id, key, value):
        print id, key, value

    cpdef run_script(self, char * script, runtime=1):
        '''
        Run a DTrace script for a number of seconds defined by the runtime.

        After the run is complete the aggregate is walked. During execution the
        stdout of DTrace is redirected to the chew, chewrec and buffered output
        writer.

        script -- The script to run.
        runtime -- The time the script should run in second (Default: 1s).
        '''
        # set simple output callbacks
        if dtrace_handle_buffered(self.handle, & buf_out, <void *>self.out_func) == -1:
            raise Exception('Unable to set the stdout buffered writer.')

        # compile
        cdef dtrace_prog_t * prg
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
            dtrace_work(self.handle, NULL, & chew, & chewrec, NULL)

            time.sleep(1)
            i += 1

        dtrace_stop(self.handle)

        # sorting instead of dtrace_aggregate_walk
        if dtrace_aggregate_walk_valsorted(self.handle, & walk, <void *>self.walk_func) != 0:
            raise Exception('Failed to walk the aggregate: ',
                            dtrace_errmsg(NULL, dtrace_errno(self.handle)))


