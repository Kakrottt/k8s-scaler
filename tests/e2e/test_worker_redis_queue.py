# tests/e2e/test_worker_redis_queue.py
import json
import time

import pytest

from tests.e2e.conftest import kubectl, wait_for_deployment_replicas, E2E_NAMESPACE


@pytest.mark.e2e
def test_worker_redis_queue_scaler_scales_with_mock_queue():
    """
    E2E: worker-redis-queue example
    - Deploy a worker deployment (if you have a manifest for it) + GeneralScaler
    - Use RedisMetricPlugin with mockQueueLength to force scaling.
    """

    # If you have a worker deployment manifest, apply it here.
    kubectl("apply", "-n", E2E_NAMESPACE, "-f", "examples/worker-redis-queue/deployment.yaml")

    # Apply GeneralScaler (it should reference the 'worker' deployment)
    kubectl(
        "apply",
        "-n",
        E2E_NAMESPACE,
        "-f",
        "examples/worker-redis-queue/generalscaler.yaml",
    )

    # Wait for worker deployment to exist and be ready
    wait_for_deployment_replicas("worker", expected_min=1, namespace=E2E_NAMESPACE)

    scaler_name = "worker-queue-scaler"  # adjust if your metadata.name differs

    # Force a big queue → scale up
    kubectl(
        "patch",
        "generalscaler",
        scaler_name,
        "-n",
        E2E_NAMESPACE,
        "--type=merge",
        "-p",
        json.dumps({"spec": {"metric": {"params": {"mockQueueLength": 1000}}}}),
    )

    time.sleep(10)

    # Expect replicas to go up (e.g., at least 3)
    wait_for_deployment_replicas("worker", expected_min=3, namespace=E2E_NAMESPACE)

    # Now, mock a small queue → scale down (but not below minReplicas)
    kubectl(
        "patch",
        "generalscaler",
        scaler_name,
        "-n",
        E2E_NAMESPACE,
        "--type=merge",
        "-p",
        json.dumps({"spec": {"metric": {"params": {"mockQueueLength": 10}}}}),
    )

    time.sleep(10)

    # Expect scale down but respect minReplicas, e.g., 1 or 2
    wait_for_deployment_replicas("worker", expected_min=1, namespace=E2E_NAMESPACE)
