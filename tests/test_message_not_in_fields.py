import io
import json
import logging
import unittest

import logstash_formatter


class LogMessagePositionalPlaceholderTest(unittest.TestCase):

    def setUp(self):
        self.log = logging.getLogger('test')
        self.log.setLevel(logging.DEBUG)

        self.stream = io.StringIO()

        with_stdlib_formatter = logging.StreamHandler(self.stream)
        self.log.addHandler(with_stdlib_formatter)

        handler = logging.StreamHandler(self.stream)
        handler.setFormatter(logstash_formatter.LogstashFormatter())
        handler.setLevel(logging.DEBUG)
        self.log.addHandler(handler)

    def test(self):
        self.log.debug('spam')
        lines = self.stream.getvalue().splitlines()
        # The first line is the stdlib formatter logging as plain text
        spam, rest = lines[0], lines[1:]
        self.assertEqual(spam, 'spam')
        json_text = ''.join(rest)
        json_ = json.loads(json_text)
        self.assertNotIn('message', json_['@fields'])
