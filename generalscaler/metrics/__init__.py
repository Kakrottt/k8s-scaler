# generalscaler/metrics/__init__.py
from .prometheus import PrometheusMetricPlugin
from .redis_plugin import RedisMetricPlugin
from .pubsub_plugin import PubSubMetricPlugin

PLUGIN_MAP = {
    "prometheus": PrometheusMetricPlugin,
    "redis": RedisMetricPlugin,
    "pubsub": PubSubMetricPlugin,
}

def get_metric_plugin(name: str, params: dict):
    cls = PLUGIN_MAP.get(name)
    if not cls:
        raise ValueError(f"Unknown metric plugin: {name}")
    return cls(params)
