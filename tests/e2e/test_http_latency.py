# tests/e2e/test_http_latency.py
import json
import time

import pytest

from tests.e2e.conftest import kubectl, wait_for_deployment_replicas, E2E_NAMESPACE



@pytest.mark.e2e
def test_http_latency_scaler_scales_up_and_down():
    """
    E2E: http-latency example
    - Deploy http-frontend + GeneralScaler
    - Force high latency via mockValue → scale up
    - Force low latency via mockValue → scale down
    """

    # 1) Apply app + scaler manifests
    kubectl("apply", "-n", E2E_NAMESPACE, "-f", "examples/http-latency/deployment.yaml")
    kubectl("apply", "-n", E2E_NAMESPACE, "-f", "examples/http-latency/generalscaler.yaml")

    # 2) Wait for base deployment to be ready (whatever initial replicas are)
    wait_for_deployment_replicas("http-frontend", expected_min=1, namespace=E2E_NAMESPACE)

    # 3) Read the GeneralScaler name (assumed to be 'http-latency-scaler' – adjust if needed)
    scaler_name = "http-latency-scaler"

    # 4) Patch metric.params.mockValue to a HIGH latency ( > targetValue ) → scale up
    kubectl(
        "patch",
        "generalscaler",
        scaler_name,
        "-n",
        E2E_NAMESPACE,
        "--type=merge",
        "-p",
        json.dumps(
            {
                "spec": {
                    "metric": {
                        "params": {
                            # High latency in ms – policy should want more replicas
                            "mockValue": 450
                        }
                    }
                }
            }
        ),
    )

    # Allow some time for cooldown + reconcile
    time.sleep(10)

    # Expect scale up to at least 3 replicas (adjust depending on your safety spec)
    wait_for_deployment_replicas("http-frontend", expected_min=3, namespace=E2E_NAMESPACE)

    # 5) Patch metric.params.mockValue to a LOW latency ( < targetValue ) → scale down
    kubectl(
        "patch",
        "generalscaler",
        scaler_name,
        "-n",
        E2E_NAMESPACE,
        "--type=merge",
        "-p",
        json.dumps(
            {
                "spec": {
                    "metric": {
                        "params": {
                            "mockValue": 80
                        }
                    }
                }
            }
        ),
    )

    # Let cooldown expire and reconcile
    time.sleep(10)

    # Expect scale down, but not below minReplicas (e.g., 2)
    wait_for_deployment_replicas("http-frontend", expected_min=2, namespace=E2E_NAMESPACE)
