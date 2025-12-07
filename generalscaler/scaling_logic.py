# generalscaler/scaling_logic.py
from .metrics import get_metric_plugin
from .policies import get_policy
from .safety import can_scale, apply_safety_limits


def reconcile_scaler(k8s_client, gs_body: dict):
    spec = gs_body["spec"]
    status = gs_body.get("status", {})

    target = spec["targetRef"]
    metric_spec = spec["metric"]
    policy_spec = spec["policy"]
    safety_spec = spec["safety"]

    # 1. Fetch current replicas from Deployment
    apps_v1 = k8s_client.AppsV1Api()
    dep = apps_v1.read_namespaced_deployment(
        name=target["name"],
        namespace=gs_body["metadata"]["namespace"],
    )
    current_replicas = dep.spec.replicas or 0

    # 2. Get metric value via plugin
    plugin = get_metric_plugin(metric_spec["plugin"], metric_spec.get("params"))
    metric_value = plugin.get_value()

    # 3. Compute desired from policy
    policy = get_policy(policy_spec["type"], policy_spec.get(policy_spec["type"]))
    raw_desired = policy.compute_desired_replicas(metric_value, current_replicas)

    # 4. Safety checks
    desired_safe = apply_safety_limits(raw_desired, current_replicas, safety_spec)
    last_scale_time = status.get("lastScaleTime")
    cooldown = safety_spec.get("cooldownSeconds", 60)

    should_scale = desired_safe != current_replicas and can_scale(
        last_scale_time, cooldown
    )

    result = {
        "metricValue": metric_value,
        "rawDesired": raw_desired,
        "desiredSafe": desired_safe,
        "shouldScale": should_scale,
        "currentReplicas": current_replicas,
    }
    return result
