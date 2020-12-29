"""
Unittest for ctypes based consumer.
"""

__author__ = 'tmetsch'


import unittest

from ctypes import c_char_p

from dtrace_ctypes import consumer

SCRIPT = 'dtrace:::BEGIN {trace("Hello World");}'


class TestDTraceConsumer(unittest.TestCase):
    """
    Tests ctypes based DTrace consumer.
    """

    def setUp(self):
        self.out = b''
        self.consumer = consumer.DTraceConsumer(out_func=self._get_output)

    def test_run_for_success(self):
        """
        Test for success.
        """
        self.consumer.run(SCRIPT)

    def test_run_for_sanity(self):
        """
        Test for sanity.
        """
        self.consumer.run(SCRIPT)
        self.assertEqual(self.out, b'Hello World')

    def _get_output(self, data, _arg):
        tmp = c_char_p(data.contents.dtbda_buffered).value.strip()
        self.out += tmp
        return 0
