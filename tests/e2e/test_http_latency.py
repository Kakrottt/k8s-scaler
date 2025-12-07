# tests/e2e/test_http_latency.py
import time
import subprocess
import pytest

@pytest.mark.e2e
def test_http_scaler_scales_up():
    # apply manifests (assuming kubectl configured to kind cluster)
    subprocess.check_call(["kubectl", "apply", "-f", "examples/http-latency/"])

    # wait for operator + deployment ready
    time.sleep(60)

    # here you could patch the fake Prometheus to return high latency
    # or set env var for plugin to return 400ms

    # wait for reconcile
    time.sleep(90)

    # assert deployment scaled
    out = subprocess.check_output(
        ["kubectl", "get", "deploy", "http-frontend", "-n", "demo", "-o", "jsonpath={.spec.replicas}"]
    ).decode("utf-8")
    replicas = int(out)
    assert replicas > 2
