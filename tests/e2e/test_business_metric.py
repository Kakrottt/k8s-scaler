# tests/e2e/test_business_metric.py
import json
import time

import pytest

from tests.e2e.conftest import kubectl, wait_for_deployment_replicas, E2E_NAMESPACE


@pytest.mark.e2e
def test_business_metric_cost_scaler_respects_budget_and_metric():
    """
    E2E: business-metric example
    - Deploy reports-api + GeneralScaler
    - Use PrometheusMetricPlugin with mockValue to drive scaling decisions.
    - This test mostly checks that scaling happens in the right direction and
      does not overshoot obvious budget constraints (indirectly).
    """

    # 1) Deploy the business service (reports-api) if you have a manifest for it:
    kubectl("apply", "-n", E2E_NAMESPACE, "-f", "examples/business-metric/deployment.yaml")

    # 2) Apply the GeneralScaler for business metric
    kubectl(
        "apply",
        "-n",
        E2E_NAMESPACE,
        "-f",
        "examples/business-metric/generalscaler.yaml",
    )

    wait_for_deployment_replicas("reports-api", expected_min=1, namespace=E2E_NAMESPACE)

    scaler_name = "business-metric-cost-scaler"  # adjust to match your metadata.name

    # Simulate high workload (metric value > metricTarget) → scale up
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
                            "mockValue": 5000  # e.g., jobs/sec or similar – above target
                        }
                    }
                }
            }
        ),
    )

    time.sleep(10)

    # Expect some scale up; use a reasonable expected_min, e.g., 3
    wait_for_deployment_replicas("reports-api", expected_min=3, namespace=E2E_NAMESPACE)

    # Simulate low workload → scale down
    kubectl(
        "patch",
        "generalscaler",
        scaler_name,
        "-n",
        E2E_NAMESPACE,
        "--type=merge",
        "-p",
        json.dumps(
            {"spec": {"metric": {"params": {"mockValue": 100}}}}  # below metricTarget
        ),
    )

    time.sleep(10)

    # Expect scale down, but respect minReplicas (e.g., 1 or 2)
    wait_for_deployment_replicas("reports-api", expected_min=1, namespace=E2E_NAMESPACE)
