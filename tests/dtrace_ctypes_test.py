"""
Unittest for ctypes based consumer.
"""

__author__ = 'tmetsch'

from dtrace_ctypes import consumer

import unittest

SCRIPT = 'syscall:::entry { @num[pid,execname] = count(); }'


class TestDTraceConsumer(unittest.TestCase):
    """
    Tests ctypes based DTrace consumer.
    """

    def setUp(self):
        self.out = ''
        self.consumer = consumer.DTraceConsumer(out_func=self._get_output, walk_func=self._test)

    def test_compile_for_success(self):
        self.consumer.run_script(SCRIPT)

    def _test(self, tmp, foo):
        print tmp

    def _get_output(self, value):
        self.out = value

