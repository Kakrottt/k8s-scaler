# k8s-scaler
# 🚀 GeneralScaler — Kubernetes Autoscaling Operator

GeneralScaler is a reusable Kubernetes **autoscaling operator** that can scale *any Deployment* using **pluggable metrics** (Prometheus, Redis, Pub/Sub, custom business metrics) and **pluggable policies** (SLO-based, cost-aware).  
It adds **safe scaling** via cooldowns, step limits, and min/max replica limits — with **unit + e2e test coverage**.

---

## ✨ Features

| Feature | Status |
|--------|--------|
| CRD + controller (Kopf / Python) | ✅ |
| Pluggable metric plugins (Prometheus / Redis / PubSub / custom) | ✅ |
| Policies (SLO / Cost) | ✅ |
| Safety: cooldown, step limits, min/max replicas | ✅ |
| Unit tests | ✅ |
| E2E tests (KinD / GKE) | ✅ |
| Helm chart | ✅ |
| CI pipeline | 🟢 |

---

## 📦 Installation

```bash
helm install general-scaler ./chart \
  --namespace general-scaler \
  --create-namespace
```
To uninstall:
```bash
helm uninstall general-scaler -n general-scaler
```

---

## 🧠 How it Works

1. Create a `GeneralScaler` CRD.
2. Operator retrieves metrics from a plugin (Prometheus / Redis / PubSub / custom).
3. Scaling policy computes raw desired replicas.
4. Safety filters (cooldown, steps, min/max) compute final desired replicas.
5. Operator patches Deployment.spec.replicas accordingly.

```
GeneralScaler → Metric Plugin → Policy → Safety → Deployment.spec.replicas
```

---

## 🔧 Usage Examples

### 1️⃣ HTTP App — Prometheus latency

```bash
kubectl apply -n demo -f examples/http-latency/deployment.yaml
kubectl apply -n demo -f examples/http-latency/generalscaler.yaml
```
Mock mode (no Prometheus needed):
```yaml
params:
  mockValue: 450
```

### 2️⃣ Worker — Redis queue length

```bash
kubectl apply -n demo -f examples/worker-redis-queue/worker-deployment.yaml
kubectl apply -n demo -f examples/worker-redis-queue/generalscaler.yaml
```
Mock mode:
```yaml
params:
  mockQueueLength: 1000
```

### 3️⃣ Business Metric — Cost-aware scaling

```bash
kubectl apply -n demo -f examples/business-metric/deployment.yaml
kubectl apply -n demo -f examples/business-metric/generalscaler.yaml
```

Example:
```yaml
policy:
  type: cost
  cost:
    maxMonthlyCost: 200
    costPerReplicaPerHour: 0.08
```

---

## 📚 CRD Fields Overview

| Field | Description |
|--------|-------------|
| `targetRef` | Deployment to scale |
| `metric` | Metric plugin, type & params |
| `policy` | SLO / Cost |
| `safety` | Cooldown, min/max, step limits |
| `status` | Last metric & scaling decision |

---

## 🧪 Development

Install deps:
```bash
pip install -r requirements.txt
```

Run unit tests:
```bash
pytest tests/unit -m unit
```

Run e2e tests (cluster required):
```bash
pytest tests/e2e -m e2e -vv
```

Formatting & lint:
```bash
black generalscaler tests
flake8 generalscaler tests
```

---

## 🔁 CI Pipeline

The workflow validates the operator through:

1. Black + flake8
2. Unit tests
3. Build Docker image
4. Create KinD cluster
5. Push image to KinD
6. Install Helm chart
7. Run e2e tests

---

## 🧩 Creating Custom Plugins

Metric plugin:
```python
from generalscaler.metrics import MetricPlugin
class MyPlugin(MetricPlugin):
    def get_value(self) -> float:
        return ...
```

Policy:
```python
from generalscaler.policies import Policy
class MyPolicy(Policy):
    def compute_desired(self, metric_value: float, current_replicas: int) -> int:
        return ...
```

---
