from ctypes import cdll, CDLL, byref, c_int, c_char_p

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
# TODO

# 4. compile
prg = LIBRARY.dtrace_program_strcompile (handle, d, 3, 4, 0, None)

# 5. run
LIBRARY.dtrace_program_exec(handle, prg, None)
LIBRARY.dtrace_go(handle)
LIBRARY.dtrace_stop(handle)

# do work and output to file
LIBRARY.dtrace_sleep(handle)
LIBRARY.dtrace_aggregate_print(handle, "out.txt", None);

txt = LIBRARY.dtrace_errmsg(handle, LIBRARY.dtrace_errno(handle))
print c_char_p(txt).value

# Last: close handle!
LIBRARY.dtrace_close(handle);
