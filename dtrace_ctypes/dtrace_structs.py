"""
The DTrace data structures.

Created on Oct 10, 2011

@author: tmetsch
"""

# disabling 'too few public meth' pylint check (R0903)
# disabling 'Invalid name' pylint check (C0103)
# pylint: disable=R0903,C0103

from ctypes import (c_int64, c_size_t, c_uint16, c_uint32, c_uint64, POINTER,
                    Structure, c_int, c_void_p, c_char_p, c_char, c_uint)


class dtrace_hdl(Structure):
    pass


class dtrace_prog(Structure):
    pass


dtrace_hdl_t = POINTER(dtrace_hdl)
dtrace_prog_t = POINTER(dtrace_prog)

class dtrace_recdesc(Structure):
    """
    sys/dtrace.h:931
    """
    _fields_ = [
        ("dtrd_action", c_uint16),  # dtrace_actkind_t
        ("dtrd_size", c_uint32),
        ("dtrd_offset", c_uint32),
        ("dtrd_alignment", c_uint16),
        ("dtrd_format", c_uint16),
        ("dtrd_arg", c_uint64),
        ("dtrd_uarg", c_uint64)]


class dtrace_aggdesc(Structure):
    """
    sys/dtrace.h:950
    """
    _fields_ = [("dtagd_name", c_char_p),
                ("dtagd_varid", c_int64),  # dtrace_aggvarid_t
                ("dtagd_flags", c_int),
                ("dtagd_id", c_void_p),  # dtrace_aggid_t
                ("dtagd_epid", c_void_p),  # dtrace_epid_t
                ("dtagd_size", c_uint32),
                ("dtagd_nrecs", c_int),
                ("dtagd_pad", c_uint32),
                ("dtagd_rec", dtrace_recdesc),  # variable-length
                ]


class dtrace_probedesc(Structure):
    """
    As defined in sys/dtrace.h:884
    """
    _fields_ = [("dtrace_id_t", c_uint),
                ("dtpd_provider", c_char),
                ("dtpd_mod", c_char),
                ("dtpd_func", c_char_p),
                ("dtpd_name", c_char_p)]


class dtrace_aggdata(Structure):
    """
    As defined in dtrace.h:351
    """
    _fields_ = [("dtada_handle", dtrace_hdl_t),
                ("dtada_desc", POINTER(dtrace_aggdesc)),
                ("dtada_edesc", c_void_p),
                ("dtada_pdesc", POINTER(dtrace_probedesc)),
                ("dtada_data", c_void_p),
                ("dtada_normal", c_uint64),
                ("dtada_size", c_size_t),
                ("dtada_delta", c_void_p),
                ("dtada_percpu", c_void_p),
                ("dtada_percpu_delta", c_void_p),
                ("dtada_total", c_int64),
                ("dtada_minbin", c_uint16),
                ("dtada_maxbin", c_uint16),
                ("dtada_flags", c_uint32)]


class dtrace_probedata(Structure):
    """
    As defined in dtrace.h:186
    """
    _fields_ = [("dtpda_handle", dtrace_hdl_t),
                ("dtpda_edesc", c_void_p),
                ("dtpda_pdesc", POINTER(dtrace_probedesc)),
                ("dtpda_cpu", c_int),
                ("dtpda_data", c_void_p),
                ("dtpda_flow", c_int),  # dtrace_flowkind_t
                ("dtpda_prefix", c_char_p),
                ("dtpda_indent", c_int)]


class dtrace_bufdata(Structure):
    """
    As defined in dtrace.h:310
    """
    _fields_ = [("dtbda_handle", dtrace_hdl_t),
                ("dtbda_buffered", c_char_p),
                ("dtbda_probe", POINTER(dtrace_probedata)),
                ("dtbda_recdesc", POINTER(dtrace_recdesc)),
                ("dtbda_aggdata", POINTER(dtrace_aggdata)),
                ("dtbda_flags", c_uint)]


DTRACE_WORKSTATUS_ERROR = -1
DTRACE_WORKSTATUS_OKAY = 0
DTRACE_WORKSTATUS_DONE = 1
