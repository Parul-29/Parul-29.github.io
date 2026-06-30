# Cloud Native Microservices Platform on AWS

Architecture and Technical Overview  
Parul Inamdar

## Project Overview

This project is a FastAPI backend that models a reproducible AWS microservices platform. It accepts service specifications, environment details, EKS cluster metadata, security settings, and observability preferences, then generates a deployment plan with readiness findings.

The backend is designed as a portfolio proof of concept for platform engineering work. It does not provision real AWS resources directly. Instead, it represents the control-plane logic that would sit in front of Terraform, Kubernetes manifests, ECR, IAM, KMS, Prometheus, Grafana, Datadog, and CloudWatch.

## Repository Contents

```text
app/
  main.py                   FastAPI application and API routes
  models.py                 Pydantic schemas for platforms, services, plans, and findings
  platform_engine.py        Deployment planning and readiness analysis
  storage.py                In-memory deployment storage
  config.py                 Environment-based settings
examples/
  sample_platform.json      Ready-to-run platform payload
requirements.txt            Python dependencies
.env.example                Optional local environment settings
```

## System Architecture

```text
Engineer submits platform request
        |
        v
FastAPI Platform API
        |
        v
Platform Engine
Builds deployment plan for services, ECR, EKS, IAM, KMS, and observability
        |
        v
Readiness Analyzer
Checks redundancy, autoscaling, public exposure, encryption, IRSA, and monitoring
        |
        v
Deployment Output
Plan, readiness score, findings, recommendations, and deployment status
```

## Component Breakdown

| Component | Technology | Responsibility |
| --- | --- | --- |
| API Layer | FastAPI | Exposes platform planning, simulated deployment, lookup, and health endpoints |
| Service Model | Pydantic | Captures image, replicas, CPU, memory, port, exposure, and autoscaling |
| Platform Engine | Python | Builds deployment plans for microservices and cloud platform modules |
| Readiness Analyzer | Python rules | Checks operational, security, and scalability risks before deployment |
| Infrastructure Plan | Terraform-oriented model | Represents VPC, EKS, ECR, IAM, KMS, and observability modules |
| Storage | In-memory store | Keeps generated deployment plans for local demos |

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
POST /api/v1/platforms/plan
POST /api/v1/platforms/deploy
GET  /api/v1/deployments
GET  /api/v1/deployments/{deployment_id}
```

## Example Platform Request

Use [examples/sample_platform.json](examples/sample_platform.json) as a ready-to-run payload.

```json
{
  "platform_name": "commerce-platform",
  "environment": "staging",
  "aws_region": "us-west-2",
  "eks_cluster": "commerce-staging-eks",
  "vpc_id": "vpc-0123456789abcdef0",
  "services": [
    {
      "name": "orders-api",
      "image": "123456789012.dkr.ecr.us-west-2.amazonaws.com/orders-api:v1",
      "replicas": 3,
      "cpu_millicores": 500,
      "memory_mb": 1024,
      "port": 8080,
      "exposure": "internal",
      "autoscaling_enabled": true
    }
  ],
  "enable_observability": true,
  "enable_kms_encryption": true,
  "enable_irsa": true
}
```

## Key Technical Challenges and Solutions

### Reproducible Cloud Infrastructure

- Modeled Terraform modules for VPC, EKS, ECR, IAM, KMS, and observability.
- Generated predictable Kubernetes manifest paths per namespace and service.
- Kept platform inputs structured so the same request can produce repeatable plans across environments.

### Security Baselines

- Added checks for KMS encryption and IAM Roles for Service Accounts.
- Flagged risky public service exposure and non-standard public ports.
- Encouraged least-privilege workload identity instead of broad node-role permissions.

### Scalability and Reliability

- Checked production replica redundancy.
- Flagged services without autoscaling.
- Included observability outputs for dashboards, container insights, and APM.

## Outcomes

| Metric | Result |
| --- | --- |
| Deployment Coverage | EKS services, ECR repositories, Kubernetes manifests, IAM roles, KMS, and observability |
| Security Controls | KMS encryption, IRSA, exposure review, and least-privilege recommendations |
| Reliability Controls | Replica checks, autoscaling validation, and deployment readiness scoring |
| Operational Output | Deployment plan, readiness score, findings, and remediation guidance |

## Technology Stack

| Category | Tools and Technologies |
| --- | --- |
| API Backend | Python, FastAPI, Pydantic |
| Cloud Platform | AWS, EKS, ECR, IAM, KMS, VPC |
| Infrastructure | Terraform, Kubernetes manifests, Docker |
| Observability | Prometheus, Grafana, Datadog, CloudWatch |
