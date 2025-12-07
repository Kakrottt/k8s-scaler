# generalscaler/safety.py
from datetime import datetime, timezone

def now_utc():
    return datetime.now(timezone.utc)

def can_scale(last_scale_time: str | None, cooldown_seconds: int) -> bool:
    if not last_scale_time:
        return True
    last = datetime.fromisoformat(last_scale_time)
    elapsed = (now_utc() - last).total_seconds()
    return elapsed >= cooldown_seconds

def apply_safety_limits(
    desired: int,
    current: int,
    safety_spec: dict,
) -> int:
    min_r = safety_spec["minReplicas"]
    max_r = safety_spec["maxReplicas"]
    max_up = safety_spec.get("maxScaleUpStep", 5)
    max_down = safety_spec.get("maxScaleDownStep", 5)

    # clamp between min/max
    desired = max(min_r, min(max_r, desired))

    delta = desired - current
    if delta > 0:
        delta = min(delta, max_up)
    elif delta < 0:
        delta = max(delta, -max_down)

    return current + delta
