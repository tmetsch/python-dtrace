'''
The implementation of the consumer.

Created on Oct 10, 2011

@author: tmetsch
'''

from ctypes import cdll, CDLL, byref, c_int, c_char_p, CFUNCTYPE, c_void_p, \
    POINTER, cast
from dtrace.dtrace_structs import dtrace_bufdata, dtrace_probedata, \
    dtrace_aggdata, dtrace_recdesc
import time

cdll.LoadLibrary("libdtrace.so")

LIBRARY = CDLL("libdtrace.so")


def simple_chew_func(data, arg):
    '''
    Callback for chew.
    '''
    print 'CPU :', c_int(data.contents.dtpda_cpu).value
    return 0


def simple_chewrec_func(data, rec, arg):
    '''
    Callback for record chewing.
    '''
    if rec == None:
        return 1
    return 0


def simple_buffered_out_writer(bufdata, arg):
    '''
    In case dtrace_work is given None as filename - this one is called.
    '''
    tmp = c_char_p(bufdata.contents.dtbda_buffered).value.strip()
    print 'out >', tmp
    return 0


def simple_walk(data, arg):
    '''
    Aggregate walker.
    '''

    # TODO: pickup the 16 and 272 from offset in desc...

    tmp = data.contents.dtada_data
    name = cast(tmp + 16, c_char_p).value
    instance = deref(tmp + 272, c_int).value

    print '{0:60s} :{1:10d}'.format(name, instance)

    return 0


def deref(addr, typ):
    '''
    Deref a pointer.
    '''
    return cast(addr, POINTER(typ)).contents


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


class DTraceConsumer(object):
    '''
    A Pyton based DTrace consumer.
    '''

    def __init__(self):
        '''
        Constructor. will get the DTrace handle
        '''
        # get dtrace handle
        self.handle = LIBRARY.dtrace_open(3, 0, byref(c_int(0)))
        if self.handle == None:
            raise Exception('Unable to get a DTrace handle.')

        # set buffer options
        if LIBRARY.dtrace_setopt(self.handle, 'bufsize', '4m') != 0:
            raise Exception(self._get_error_msg())

        if LIBRARY.dtrace_setopt(self.handle, 'aggsize', '4m') != 0:
            raise Exception(self._get_error_msg())

    def __del__(self):
        '''
        Always close the DTrace handle :-)
        '''
        LIBRARY.dtrace_close(self.handle)

    def run_script(self, script, runtime=1, chew_func=None,
                                            chew_rec_func=None,
                                            walk_func=None,
                                            out_func=None):
        '''
        Run a DTrace script for a number of seconds defined by the runtime.

        After the run is complete the aggregate is walked. During execution the
        stdout of DTrace is redirected to the chew, chewrec and buffered output
        writer.

        script -- The script to run.
        runtime -- The time the script should run in second (Default: 1s).
        '''
        if chew_func is not None:
            chew = CHEW_FUNC(chew_func)
        else:
            chew = CHEW_FUNC(simple_chew_func)

        if chew_rec_func is not None:
            chew_rec = CHEWREC_FUNC(chew_rec_func)
        else:
            chew_rec = CHEWREC_FUNC(simple_chewrec_func)

        if walk_func is not None:
            walk = WALK_FUNC(walk_func)
        else:
            walk = WALK_FUNC(simple_walk)

        if out_func is not None:
            buf_out = BUFFERED_FUNC(out_func)
        else:
            buf_out = BUFFERED_FUNC(simple_buffered_out_writer)


        # set simple output callbacks
        if LIBRARY.dtrace_handle_buffered(self.handle, buf_out, None) == -1:
            raise Exception('Unable to set the stdout buffered writer.')

        # compile
        prg = LIBRARY.dtrace_program_strcompile(self.handle,
                                                     script, 3, 4, 0, None)
        if prg == None:
            raise Exception('Unable to compile the script: ',
                            self._get_error_msg())

        # run
        if LIBRARY.dtrace_program_exec(self.handle, prg, None) == -1:
            raise Exception('Failed to execute: ', self._get_error_msg())
        if LIBRARY.dtrace_go(self.handle) != 0:
            raise Exception('Failed to run_script: ', self._get_error_msg())

        # aggregate data for a few sec...
        i = 0
        while i < runtime:
            LIBRARY.dtrace_sleep(self.handle)
            LIBRARY.dtrace_work(self.handle, None, chew, chew_rec, None)

            time.sleep(1)
            i += 1

        LIBRARY.dtrace_stop(self.handle)

        # sorting instead of dtrace_aggregate_walk
        if LIBRARY.dtrace_aggregate_walk_valsorted(self.handle, walk,
                                                   None) != 0:
            raise Exception('Failed to walk the aggregate: ',
                            self._get_error_msg())

    def _get_error_msg(self):
        txt = LIBRARY.dtrace_errmsg(self.handle,
                                    LIBRARY.dtrace_errno(self.handle))
        return c_char_p(txt).value
