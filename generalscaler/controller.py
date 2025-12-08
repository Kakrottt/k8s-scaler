# generalscaler/controller.py
import kopf
import logging
from kubernetes import config, client as k8s_client
from kubernetes.config.config_exception import ConfigException

from .scaling_logic import reconcile_scaler
from .safety import now_utc


# config.load_incluster_config()
# k8s = k8s_client
def load_kube_config():
    try:
        # Try in-cluster first (for when this runs inside Kubernetes)
        config.load_incluster_config()
        print("Loaded in-cluster Kubernetes config")
    except ConfigException:
        # Fallback to local kubeconfig (for dev on your laptop)
        config.load_kube_config()
        print("Loaded local kubeconfig (e.g. ~/.kube/config)")


@kopf.on.startup()
def configure(settings: kopf.OperatorSettings, **_):
    # Call this once at import time
    load_kube_config()
    settings.posting.level = logging.INFO
    # logging.getLogger().setLevel(logging.INFO)


@kopf.on.create("generalscalers", group="scaling.devsecops.ai", version="v1alpha1")
@kopf.on.update("generalscalers", group="scaling.devsecops.ai", version="v1alpha1")
@kopf.timer(
    "generalscalers", group="scaling.devsecops.ai", version="v1alpha1", interval=30.0
)
def reconcile(body, spec, status, namespace, logger, patch, **kwargs):
    status = status or {}
    result = reconcile_scaler(k8s_client, body)

    logger.info(
        f"metric={result['metricValue']} "
        f"raw={result['rawDesired']} safe={result['desiredSafe']} "
        f"current={result['currentReplicas']} scale={result['shouldScale']}"
    )

    if result["shouldScale"]:
        apps = k8s_client.AppsV1Api()
        target = spec["targetRef"]
        desired = result["desiredSafe"]

        body_patch = {"spec": {"replicas": desired}}
        apps.patch_namespaced_deployment(
            name=target["name"],
            namespace=namespace,
            body=body_patch,
        )
        last_scale_time = now_utc().isoformat()
        last_reason = f"Metric {spec['metric']['type']}={result['metricValue']}"
        desired_replicas = desired
    else:
        last_scale_time = status.get("lastScaleTime")
        last_reason = status.get("lastScaleReason")
        desired_replicas = status.get("desiredReplicas", result["currentReplicas"])

    # return {
    #     "status": {
    #         "currentReplicas": result["currentReplicas"],
    #         "desiredReplicas": desired_replicas,
    #         "lastMetricValue": result["metricValue"],
    #         "lastScaleTime": last_scale_time,
    #         "lastScaleReason": last_reason,
    #     }
    # }
    # "Patching failed with inconsistencies" warnings.
    patch.status["currentReplicas"] = result["currentReplicas"]
    patch.status["desiredReplicas"] = desired_replicas
    patch.status["lastMetricValue"] = result["metricValue"]
    patch.status["lastScaleTime"] = last_scale_time
    patch.status["lastScaleReason"] = last_reason
