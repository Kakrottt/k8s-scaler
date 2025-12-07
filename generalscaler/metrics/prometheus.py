# generalscaler/metrics/prometheus.py
import requests
from .base import MetricPlugin


class PrometheusMetricPlugin(MetricPlugin):
    def get_value(self) -> float:
        # 1) Pure mock mode – no HTTP call, no baseUrl/query needed
        if "mockValue" in self.params:
            return float(self.params["mockValue"])

        # 2) Real Prometheus query mode
        base_url = self.params["baseUrl"]  # e.g. http://prometheus.monitoring:9090
        query = self.params["query"]       # e.g. histogram_quantile(...)

        resp = requests.get(
            f"{base_url}/api/v1/query",
            params={"query": query},
            timeout=5,
        )
        resp.raise_for_status()
        data = resp.json()

        result = data["data"]["result"]
        if not result:
            raise RuntimeError("Prometheus query returned no results")

        value_str = result[0]["value"][1]
        return float(value_str)
