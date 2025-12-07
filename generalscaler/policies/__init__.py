# generalscaler/policies/__init__.py
from .slo import SLOPolicy
from .cost import CostPolicy

POLICY_MAP = {
    "slo": SLOPolicy,
    "cost": CostPolicy,
}

def get_policy(name: str, spec: dict):
    cls = POLICY_MAP.get(name)
    if not cls:
        raise ValueError(f"Unknown policy type: {name}")
    return cls(spec)
