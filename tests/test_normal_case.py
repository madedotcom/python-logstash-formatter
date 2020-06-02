import io
import json
import logging
import os
import pprint
import unittest

import icdiff_inprocess
import logstash_formatter


class TestCase(unittest.TestCase):

    nr_cols = 80

    def assertEqualDiff(self, got, expected, canonicalize=lambda json_: json_):
        canonicalize(expected)
        canonicalize(got)

        if isinstance(expected, str):
            expected = expected
        else:
            expected = pprint.pformat(expected)
        if isinstance(got, str):
            got = got
        else:
            got = pprint.pformat(got)

        # I'm sure I'm supposed to do something different here but this will do
        if got != expected:
            diff = icdiff_inprocess.diff_text(
                expected, got, nr_cols=self.nr_cols
            )
            print(diff)
            print(got)
            self.fail()


class Test(TestCase):

    def setUp(self):
        self.stream = io.StringIO()
        handler = logging.StreamHandler(self.stream)
        handler.setFormatter(logstash_formatter.LogstashFormatter())
        handler.setLevel(logging.DEBUG)
        self.log = logging.getLogger('test')
        self.log.addHandler(handler)
        self.log.setLevel(logging.DEBUG)

    def canonicalize(self, json_):
        def lookup(name):
            if name.startswith("@fields."):
                _, _, name = name.partition("@fields.")
                dict_ = json_["@fields"]
            else:
                dict_ = json_
            return name, dict_

        def censor(name, expected_type=None):
            name, dict_ = lookup(name)
            if name not in dict_:
                print('Missing name', name, dict_)
                return

            if expected_type:
                self.assertEqual(expected_type, type(dict_[name]))
            dict_[name] = '<censored>'

        censor('@fields.created', float)
        censor('@fields.lineno', int)
        censor('@fields.msecs', float)
        censor('@fields.pathname', str)
        censor('@fields.process', int)
        censor('@fields.relativeCreated', float)
        censor('@fields.thread', int)
        censor('@source_host', str)
        censor('@timestamp', str)
        censor('@monotonic_timestamp', int)

    def test(self):
        self.log.debug('spam')
        self.assertEqualDiff(
            json.loads(self.stream.getvalue()),
            {
                '@fields': {
                    'args': [],
                    'created': 1496407610.9405103,
                    'filename': 'test_normal_case.py',
                    'funcName': 'test',
                    'levelname': 'DEBUG',
                    'levelno': 10,
                    'lineno': 50,
                    'module': 'test_normal_case',
                    'msecs': 940.5102729797363,
                    'name': 'test',
                    'pathname': '/path/to/test_normal_case.py',
                    'process': 22318,
                    'processName': 'MainProcess',
                    'relativeCreated': 1474.8973846435547,
                    'stack_info': None,
                    'thread': 139845871032064,
                    'threadName': 'MainThread',
                },
                '@message': 'spam',
                '@source_host': 'fred',
                '@timestamp': '2017-06-02T12:46:50.940578Z',
                "@monotonic_timestamp": 12345676789,
            },
            canonicalize=self.canonicalize
        )
