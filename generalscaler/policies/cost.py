# generalscaler/policies/cost.py
import math
from datetime import datetime
from .base import Policy

class CostPolicy(Policy):
    """
    Very simplified cost-aware policy:
    - ensures total projected hourly cost <= budget (converted from monthly)
    - but still uses metric target to avoid underprovisioning
    """
    def compute_desired_replicas(self, metric_value: float, current_replicas: int) -> int:
        metric_target = self.spec.get("metricTarget", metric_value or 1)
        base_desired = max(1, int(math.ceil(metric_value / metric_target)))

        max_monthly = self.spec.get("maxMonthlyCost")
        cost_per_replica_hour = self.spec.get("costPerReplicaPerHour")

        if not max_monthly or not cost_per_replica_hour:
            return base_desired

        # approx 730 hours / month
        max_replicas_budget = int(max_monthly / (cost_per_replica_hour * 730) or 1)
        return min(base_desired, max_replicas_budget)
