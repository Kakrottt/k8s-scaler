# tests/unit/test_safety.py
import pytest
from generalscaler.safety import apply_safety_limits


@pytest.mark.unit
def test_respects_min_max_and_steps():
    safety = {
        "minReplicas": 1,
        "maxReplicas": 10,
        "maxScaleUpStep": 2,
        "maxScaleDownStep": 1,
    }
    assert apply_safety_limits(20, current=1, safety_spec=safety) == 3  # +2
    assert apply_safety_limits(0, current=5, safety_spec=safety) == 4  # -1
