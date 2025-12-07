# generalscaler/metrics/redis_plugin.py
import redis
from .base import MetricPlugin

class RedisMetricPlugin(MetricPlugin):
    def __init__(self, params: dict):
        super().__init__(params)
        self.client = redis.Redis(
            host=self.params.get("host", "redis"),
            port=int(self.params.get("port", 6379)),
            db=int(self.params.get("db", 0)),
        )

    def get_value(self) -> float:
        key = self.params["key"]  # queue key
        length = self.client.llen(key)
        return float(length)
