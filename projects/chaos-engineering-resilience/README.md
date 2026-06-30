# Chaos Engineering for Cloud-Native Resilience

Architecture and Technical Overview  
Parul Inamdar

## Project Overview

This project is a FastAPI backend for planning and evaluating controlled chaos experiments against cloud-native services. It turns resilience research into a practical API that defines failure scenarios, steady-state hypotheses, blast-radius limits, guardrails, observed metrics, and improvement recommendations.

The backend is intentionally safe for a portfolio proof of concept: it simulates experiment outcomes instead of disrupting real infrastructure. The same API shape can later connect to Kubernetes, AWS Fault Injection Service, LitmusChaos, Gremlin, Prometheus, Grafana, Datadog, or CloudWatch.

## Repository Contents

```text
app/
  main.py                   FastAPI application and API routes
  models.py                 Pydantic schemas for experiments, metrics, and findings
  experiment_engine.py      Experiment planning and simulated execution logic
  resilience.py             Steady-state and guardrail evaluation
  storage.py                In-memory experiment store
  config.py                 Environment-based settings
examples/
  sample_experiment.json    Ready-to-run experiment payload
requirements.txt            Python dependencies
.env.example                Optional local environment settings
```

## System Architecture

```text
Engineer defines resilience hypothesis
        |
        v
Experiment API receives target, failure type, blast radius, and guardrails
        |
        v
Experiment Engine
Plans or simulates a controlled failure experiment
        |
        v
Resilience Analyzer
Compares observed metrics against steady-state expectations
        |
        v
Decision Layer
Completed or aborted result, resilience score, findings, recommendations
```

## Component Breakdown

| Component | Technology | Responsibility |
| --- | --- | --- |
| API Layer | FastAPI | Exposes experiment planning, execution, lookup, and health endpoints |
| Experiment Model | Pydantic | Defines target service, failure type, hypothesis, guardrails, and metrics |
| Experiment Engine | Python | Simulates controlled failures and produces measurable outcomes |
| Resilience Analyzer | Python rules | Checks availability, latency, error rate, replica health, and recovery metrics |
| Safety Controls | Guardrails | Aborts experiments when configured thresholds are breached |
| Storage | In-memory store | Keeps planned and executed experiment results for local demos |

## Run Locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

```text
GET  /health
POST /api/v1/experiments/plan
POST /api/v1/experiments/run
GET  /api/v1/experiments
GET  /api/v1/experiments/{experiment_id}
```

## Example Experiment Request

Use [examples/sample_experiment.json](examples/sample_experiment.json) as a ready-to-run payload.

```json
{
  "title": "Checkout API latency resilience",
  "target": {
    "service": "checkout-api",
    "environment": "staging",
    "namespace": "commerce",
    "replicas": 4,
    "criticality": "high"
  },
  "failure_type": "latency_injection",
  "duration_seconds": 300,
  "blast_radius_percent": 30,
  "hypothesis": {
    "availability_percent": 99.0,
    "p95_latency_ms": 500,
    "error_rate_percent": 1.0,
    "minimum_healthy_replicas": 2
  }
}
```

## Key Technical Challenges and Solutions

### Keeping Experiments Safe

- Added blast-radius percentages to scope the size of a failure.
- Added guardrails that abort experiments when availability, error rate, latency, or replica health cross unsafe thresholds.
- Used simulated execution for the portfolio backend so the API can be demonstrated without affecting real infrastructure.

### Making Resilience Measurable

- Modeled steady-state expectations for availability, p95 latency, error rate, and healthy replicas.
- Returned detection time, recovery time, and a resilience score for each experiment.
- Converted metric failures into actionable findings and recommendations.

### Connecting Research to Practice

- Used cloud outage research themes such as cascading failures and slow detection as measurable experiment outcomes.
- Mapped chaos engineering methods to service crash, latency, partition, dependency outage, CPU pressure, and memory pressure scenarios.

## Outcomes

| Metric | Result |
| --- | --- |
| Failure Coverage | Service crash, latency, network partition, dependency outage, CPU pressure, and memory pressure |
| Safety Controls | Guardrails, blast-radius limits, and abort status |
| Resilience Metrics | Availability, p95 latency, error rate, healthy replicas, detection time, and recovery time |
| Engineering Output | Risk findings, resilience score, and improvement recommendations |

## Technology Stack

| Category | Tools and Technologies |
| --- | --- |
| API Backend | Python, FastAPI, Pydantic |
| Resilience Logic | Rule-based steady-state and guardrail evaluation |
| Cloud-Native Concepts | Kubernetes services, microservices, observability, blast radius |
| Future Integrations | AWS FIS, LitmusChaos, Prometheus, Grafana, Datadog, CloudWatch |
