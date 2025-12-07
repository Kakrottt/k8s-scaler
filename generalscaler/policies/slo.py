# generalscaler/policies/slo.py
import math
from .base import Policy


class SLOPolicy(Policy):
    """
    Simple: if metric > objective => scale up; if < objective => scale down
    Using proportional adjustment with clamping by safety later.
    """

    def compute_desired_replicas(
        self, metric_value: float, current_replicas: int
    ) -> int:
        slo_obj = self.spec["objective"]
        if slo_obj <= 0:
            return current_replicas

        # ratio > 1 => metric worse than SLO, need more replicas
        ratio = metric_value / slo_obj
        # simple proportional: new = current * ratio
        desired = max(1, int(math.ceil(current_replicas * ratio)))
        return desired
