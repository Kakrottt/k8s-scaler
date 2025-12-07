# tests/unit/test_slo_policy.py
import pytest
from generalscaler.policies.slo import SLOPolicy

@pytest.mark.unit
def test_slo_policy_scales_up():
    policy = SLOPolicy({"objective": 200})
    desired = policy.compute_desired_replicas(metric_value=400, current_replicas=2)
    assert desired >= 3  # doubles due to ratio 2x

@pytest.mark.unit
def test_slo_policy_scales_down():
    policy = SLOPolicy({"objective": 200})
    desired = policy.compute_desired_replicas(metric_value=100, current_replicas=4)
    assert desired <= 3
