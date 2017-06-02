import io
import logging
import unittest

import logstash_formatter


class LogMessagePositionalPlaceholderTest(unittest.TestCase):

    def setUp(self):
        self.stream = io.StringIO()
        handler = logging.StreamHandler(self.stream)
        handler.setFormatter(logstash_formatter.LogstashFormatter())
        handler.setLevel(logging.DEBUG)
        self.log = logging.getLogger('test')
        self.log.addHandler(handler)
        self.log.setLevel(logging.DEBUG)

    def assertLogMessage(self, msg):
        self.assertTrue(
            '"@message": "{}"'.format(msg) in self.stream.getvalue())

    def do_test(self, msg):
        self.log.debug(msg)
        self.assertLogMessage(msg)

    def test_normal_log_message(self):
        self.do_test('foo')

    def test_implicit_positional_placeholder(self):
        self.do_test('{}')

    def test_explicit_positional_placeholder(self):
        self.do_test('{0}')

    def test_unbalanced_curly_brace(self):
        self.do_test('{')
