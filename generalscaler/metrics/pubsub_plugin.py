# generalscaler/metrics/pubsub_plugin.py
from google.cloud import pubsub_v1
from .base import MetricPlugin

class PubSubMetricPlugin(MetricPlugin):
    def __init__(self, params: dict):
        super().__init__(params)
        self.client = pubsub_v1.SubscriberClient()
        self.subscription_path = self.params["subscriptionPath"]

    def get_value(self) -> float:
        # Metadata / backlog is usually retrieved via API; simplified:
        stats = self.client.get_subscription(self.subscription_path)
        # In real impl, use BigQuery or monitoring; here we assume attribute:
        backlog = int(stats.message_retention_duration.seconds)  # placeholder
        return float(backlog)
