# tests/unit/test_redis_mock.py
import pytest
from generalscaler.metrics.redis_plugin import RedisMetricPlugin


@pytest.mark.unit
def test_redis_mock_queue_length():
    plugin = RedisMetricPlugin({"mockQueueLength": 123})
    assert plugin.get_value() == 123.0
