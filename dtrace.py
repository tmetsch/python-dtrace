from ctypes import *

class dtrace_bufdata(Structure):
    _fields_ = [("dtbda_handle", c_void_p),
                ("dtbda_buffered", c_char_p),
                ("dtbda_probe", c_void_p),
                ("dtbda_recdesc", c_void_p),
                ("dtbda_aggdata",c_void_p),
                ("dtbda_flags", c_uint)
        ]

class dtrace_probedesc(Structure):
    _fields_ = [("dtrace_id_t", c_uint),
                ("dtpd_provider", c_char),
                ("dtpd_mod", c_char),
                ("dtpd_func", c_char),
                ("dtpd_name", c_char * 64)]

class dtrace_probedata(Structure):
    _fields_ = [("dtpda_handle", c_void_p),
               ("dtpda_edesc", c_void_p),
               ("dtpda_pdesc", dtrace_probedesc),
               ("dtpda_cpu", c_int),
               ("dtpda_data", c_void_p),
               ("dtpda_flow", c_void_p),
               ("dtpda_prefix", c_void_p),
               ("dtpda_indent", c_int)]
    pass

class dtrace_recdesc(Structure):
    pass


CHEW_FUNC = CFUNCTYPE(c_int, POINTER(dtrace_probedata), POINTER(c_void_p))
CHEWREC_FUNC = CFUNCTYPE(c_int,
                         POINTER(dtrace_probedata),
                         POINTER(dtrace_recdesc),
                         POINTER(c_void_p))
BUFFERED_FUNC = CFUNCTYPE(c_int, POINTER(dtrace_bufdata), POINTER(c_void_p)) 

def chew_func(data, arg):
##    print dir(data.contents)
    print 'cpu :', c_int(data.contents.dtpda_cpu).value

##    print dir(data.contents.dtpda_pdesc)
##    print 'probe id :', c_uint(data.contents.dtpda_pdesc.dtrace_id_t).value
    
    #print len(data.contents.dtpda_pdesc.dtpd_name)
    #print 'probe name :', c_char(data.contents.dtpda_pdesc.dtpd_name[0])
    
    return 0

def chewrec_func(data, rec, arg):
    if rec == None:
        return 1
    return 0

def buffered(bufdata, arg):
    print c_char_p(bufdata.contents.dtbda_buffered).value.strip()
    return 0

if __name__ == '__main__':
    cdll.LoadLibrary("libdtrace.so")

    LIBRARY = CDLL("libdtrace.so")

    d = 'dtrace:::BEGIN {trace("Hello World");}'

    # 1. get dtrace handle
    handle = LIBRARY.dtrace_open(3, 0, byref(c_int(0)))

    # 2. options
    if LIBRARY.dtrace_setopt(handle, "bufsize", "4m") != 0:
        txt = LIBRARY.dtrace_errmsg(handle, LIBRARY.dtrace_errno(handle))
        raise Exception(c_char_p(txt).value)

    # 3. callbacks
    buf_func = BUFFERED_FUNC(buffered)
    LIBRARY.dtrace_handle_buffered(handle, buf_func, None)

    # 4. compile
    prg = LIBRARY.dtrace_program_strcompile (handle, d, 3, 4, 0, None)

    # 5. run
    LIBRARY.dtrace_program_exec(handle, prg, None)
    LIBRARY.dtrace_go(handle)
    LIBRARY.dtrace_stop(handle)

    # do work and output to file
    LIBRARY.dtrace_sleep(handle)
    chew = CHEW_FUNC(chew_func)
    chew_rec = CHEWREC_FUNC(chewrec_func)
    LIBRARY.dtrace_work(handle, None, chew, chew_rec, None);

    #LIBRARY.dtrace_aggregate_print(handle, "out.txt", None);

    txt = LIBRARY.dtrace_errmsg(handle, LIBRARY.dtrace_errno(handle))
    print c_char_p(txt).value

    # Last: close handle!
    LIBRARY.dtrace_close(handle);
