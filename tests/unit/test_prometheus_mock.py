# tests/unit/test_prometheus_mock.py
import pytest
from generalscaler.metrics.prometheus import PrometheusMetricPlugin


@pytest.mark.unit
def test_prometheus_mock_value():
    plugin = PrometheusMetricPlugin({"mockValue": 321})
    assert plugin.get_value() == 321.0
