#!/usr/bin/env python2.7

'''
Simple Python based DTrace consumers which executes a Hello World D script
using libdtrace and ctypes to access it.
'''
from ctypes import cdll, CDLL, Structure, c_void_p, c_char_p, c_uint, c_int, \
c_char, CFUNCTYPE, POINTER, byref


SCRIPT = 'dtrace:::BEGIN {trace("Hello World");}'


class dtrace_bufdata(Structure):
    '''
    As defined in dtrace.h:310
    '''
    _fields_ = [("dtbda_handle", c_void_p),
                ("dtbda_buffered", c_char_p),       # works
                ("dtbda_probe", c_void_p),
                ("dtbda_recdesc", c_void_p),
                ("dtbda_aggdata", c_void_p),
                ("dtbda_flags", c_uint)
        ]


class dtrace_probedesc(Structure):
    '''
    As defined in sys/dtrace.h:884
    '''
    _fields_ = [("dtrace_id_t", c_uint),
                ("dtpd_provider", c_char),
                ("dtpd_mod", c_char),
                ("dtpd_func", c_char_p),
                ("dtpd_name", c_char_p)]


class dtrace_probedata(Structure):
    '''
    As defined in dtrace.h:186
    '''
    _fields_ = [("dtpda_handle", c_void_p),
               ("dtpda_edesc", c_void_p),
               ("dtpda_pdesc", dtrace_probedesc),
               ("dtpda_cpu", c_int),                # works
               ("dtpda_data", c_void_p),
               ("dtpda_flow", c_void_p),
               ("dtpda_prefix", c_void_p),
               ("dtpda_indent", c_int)]


class dtrace_recdesc(Structure):
    '''
    As defined in sys/dtrace.h:931
    '''
    pass


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

cdll.LoadLibrary("libdtrace.so")

LIBRARY = CDLL("libdtrace.so")


def chew_func(data, arg):
    '''
    Callback for chew.
    '''
    print 'cpu :', c_int(data.contents.dtpda_cpu).value
    return 0


def chewrec_func(data, rec, arg):
    '''
    Callback for record chewing.
    '''
    if rec == None:
        return 1
    return 0


def buffered(bufdata, arg):
    '''
    In case dtrace_work is given None as filename - this one is called.
    '''
    print c_char_p(bufdata.contents.dtbda_buffered).value.strip()
    return 0


def run_dtrace():
    '''
    Go for it...
    '''
    # get dtrace handle
    handle = LIBRARY.dtrace_open(3, 0, byref(c_int(0)))

    # options
    if LIBRARY.dtrace_setopt(handle, "bufsize", "4m") != 0:
        txt = LIBRARY.dtrace_errmsg(handle, LIBRARY.dtrace_errno(handle))
        raise Exception(c_char_p(txt).value)

    # callbacks
    buf_func = BUFFERED_FUNC(buffered)
    LIBRARY.dtrace_handle_buffered(handle, buf_func, None)

    # compile
    prg = LIBRARY.dtrace_program_strcompile(handle, SCRIPT, 3, 4, 0, None)

    # run
    LIBRARY.dtrace_program_exec(handle, prg, None)
    LIBRARY.dtrace_go(handle)
    LIBRARY.dtrace_stop(handle)

    # do work
    LIBRARY.dtrace_sleep(handle)
    chew = CHEW_FUNC(chew_func)
    chew_rec = CHEWREC_FUNC(chewrec_func)
    LIBRARY.dtrace_work(handle, None, chew, chew_rec, None)

    # Get errors if any...
    txt = LIBRARY.dtrace_errmsg(handle, LIBRARY.dtrace_errno(handle))
    print c_char_p(txt).value

    # Last: close handle!
    LIBRARY.dtrace_close(handle)

if __name__ == '__main__':
    run_dtrace()
