"""
Unittest for cython based consumer.
"""

__author__ = 'tmetsch'

import unittest

import dtrace

SCRIPT = 'dtrace:::BEGIN {trace("Hello World");}'


class TestDTraceConsumer(unittest.TestCase):
    """
    Test DTrace consumer.
    """

    def setUp(self):
        self.out = ''
        self.consumer = dtrace.DTraceConsumer(out_func=self._get_output)

    # Test fo success.

    def test_compile_for_success(self):
        """
        Test for success.
        """
        self.consumer.compile(SCRIPT)

    def test_run_for_success(self):
        """
        Test for success.
        """
        self.consumer.run(SCRIPT)

    # Test fo failure.

    def test_compile_for_failure(self):
        """
        Test for failure.
        """
        self.assertRaises(Exception, self.consumer.compile, 'foo')

    def test_run_for_failure(self):
        """
        Test for failure.
        """
        self.assertRaises(Exception, self.consumer.run, 'sadf')

    # Test fo sanity.

    def test_run_for_sanity(self):
        """
        Test for sanity.
        """
        self.consumer.run(SCRIPT)
        self.assertEqual(b'Hello World', self.out)

    def _get_output(self, tmp):
        """
        Test for sanity.
        """
        self.out = tmp
