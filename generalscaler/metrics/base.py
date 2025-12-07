# generalscaler/metrics/base.py
from abc import ABC, abstractmethod


class MetricPlugin(ABC):
    def __init__(self, params: dict):
        self.params = params or {}

    @abstractmethod
    def get_value(self) -> float:
        """Return current metric value as float."""
        ...
