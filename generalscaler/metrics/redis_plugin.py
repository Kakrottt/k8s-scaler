# # generalscaler/metrics/redis_plugin.py
import redis
from .base import MetricPlugin

# class RedisMetricPlugin(MetricPlugin):
#     def __init__(self, params: dict):
#         super().__init__(params)
#         self.client = redis.Redis(
#             host=self.params.get("host", "redis"),
#             port=int(self.params.get("port", 6379)),
#             db=int(self.params.get("db", 0)),
#         )

#     def get_value(self) -> float:
#         key = self.params["key"]  # queue key
#         length = self.client.llen(key)
#         return float(length)

class RedisMetricPlugin(MetricPlugin):
    def __init__(self, params: dict):
        super().__init__(params)

        # If mock exists, DO NOT initialize Redis client at all
        if "mockQueueLength" in self.params:
            self.client = None
        else:
            self.client = redis.Redis(
                host=self.params.get("host", "redis"),
                port=int(self.params.get("port", 6379)),
                db=int(self.params.get("db", 0)),
            )

    def get_value(self) -> float:
        # 1) Serve mock immediately — nothing else should run
        if "mockQueueLength" in self.params:
            return float(self.params["mockQueueLength"])

        # 2) Real Redis mode (requires key)
        key = self.params["key"]
        length = self.client.llen(key)
        return float(length)
