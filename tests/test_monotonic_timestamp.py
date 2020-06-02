import io
import json
import logging
import time

import logstash_formatter


def get_log(stream):
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logstash_formatter.LogstashFormatter())
    handler.setLevel(logging.DEBUG)
    log = logging.getLogger('test')
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)
    return log

def test_monotonic_timestamp():
    stream = io.StringIO()
    start = time.time_ns()
    log = get_log(stream)
    log.debug('foo')
    after = time.time_ns()
    actual = json.loads(stream.getvalue())['@monotonic_timestamp']
    assert start < actual < after
