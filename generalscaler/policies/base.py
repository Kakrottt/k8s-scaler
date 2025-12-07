# generalscaler/policies/base.py
from abc import ABC, abstractmethod

class Policy(ABC):
    def __init__(self, spec: dict):
        self.spec = spec or {}

    @abstractmethod
    def compute_desired_replicas(self, metric_value: float, current_replicas: int) -> int:
        ...
