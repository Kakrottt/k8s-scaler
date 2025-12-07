# tests/e2e/conftest.py
import json
import os
import subprocess
import time

import pytest

E2E_NAMESPACE = os.environ.get("E2E_NAMESPACE", "demo")


def kubectl(*args: str) -> str:
    """Run a kubectl command and return stdout as text."""
    cmd = ["kubectl", *args]
    return subprocess.check_output(cmd, text=True)


def wait_for_deployment_replicas(
    name: str,
    expected_min: int,
    namespace: str = E2E_NAMESPACE,
    timeout: int = 300,
    poll_interval: int = 5,
):
    """Wait until spec.replicas and availableReplicas are both >= expected_min."""
    deadline = time.time() + timeout
    last_spec = last_available = None

    while time.time() < deadline:
        out = kubectl("get", "deploy", name, "-n", namespace, "-o", "json")
        data = json.loads(out)
        spec_replicas = int(data["spec"]["replicas"])
        avail_replicas = int(data["status"].get("availableReplicas") or 0)

        last_spec, last_available = spec_replicas, avail_replicas

        if spec_replicas >= expected_min and avail_replicas >= expected_min:
            return

        time.sleep(poll_interval)

    raise AssertionError(
        f"Deployment/{name} in ns={namespace} did not reach "
        f"{expected_min} replicas in time "
        f"(last spec={last_spec}, available={last_available})"
    )


@pytest.fixture(scope="session", autouse=True)
def ensure_namespace():
    """Ensure the E2E namespace exists."""
    try:
        kubectl("get", "ns", E2E_NAMESPACE)
    except subprocess.CalledProcessError:
        kubectl("create", "ns", E2E_NAMESPACE)
