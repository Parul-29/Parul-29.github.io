# Agentic AI System for DevSecOps Pipeline Automation

Architecture and Technical Overview  
Parul Inamdar

## Project Overview

This project is a multi-agent AI system built to automate security enforcement across CI/CD pipelines. When a developer pushes code to GitHub, specialized agents automatically scan for vulnerabilities, misconfigurations, and compliance violations.

A central reasoning agent can use the Ollama API to consolidate findings, assign risk scores, generate fix suggestions, and escalate critical issues to a human reviewer. The backend also works without Ollama by using deterministic scoring and routing.

## Repository Contents

```text
app/
  agents/
    vulnerability.py        Vulnerability scanner agent
    misconfiguration.py     IaC, IAM, and workflow misconfiguration scanner
    compliance.py           CI/CD and review-control compliance checker
    reasoning.py            Risk scoring, routing, and optional Ollama reasoning
  main.py                   FastAPI application and API routes
  orchestrator.py           Parallel multi-agent workflow coordinator
  models.py                 Pydantic request, response, and finding schemas
  storage.py                In-memory scan and review queue storage
examples/
  sample_scan.json          Example scan payload
requirements.txt            Python dependencies
.env.example                Optional environment settings
```

## System Architecture

```text
Developer pushes code
        |
        v
GitHub Actions webhook fires
        |
        v
Orchestrator Agent
Receives trigger, manages workflow, delegates to subagents, aggregates findings
        |
        v
Specialized Subagents run in parallel
Vulnerability Scanner | Misconfiguration Scanner | Compliance Checker
        |
        v
Findings Collector
Consolidates structured JSON findings from all agents
        |
        v
Reasoning Agent
Performs risk scoring, fix suggestions, and action routing
        |
        v
Decision and Output Layer
API response | GitHub webhook queue | Human review queue
```

## Component Breakdown

| Component | Technology | Responsibility |
| --- | --- | --- |
| Trigger Layer | GitHub webhook endpoint | Accepts push-style events |
| Orchestrator Agent | Python, asyncio | Coordinates subagents and manages workflow state |
| Vulnerability Scanner | Python rules, extensible scanner interface | Detects risky code patterns and vulnerable dependency examples |
| Misconfiguration Scanner | Custom rules | Checks Terraform, IAM policies, S3 exposure, and GitHub Actions risks |
| Compliance Checker | Policy checks | Validates CI workflow, CODEOWNERS, and token permission controls |
| Reasoning Agent | Deterministic scoring, optional Ollama API | Prioritizes risk, scores findings, and generates summary |
| Human-in-the-Loop | Review queue endpoint | Escalates Critical and High findings for review |

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
POST /api/v1/scans
GET  /api/v1/scans/{scan_id}
GET  /api/v1/review-queue
POST /api/v1/github/webhook
```

## Example Scan Request

Use [examples/sample_scan.json](examples/sample_scan.json) as a ready-to-run payload.

```json
{
  "repository": "Parul-29/sample-service",
  "branch": "main",
  "commit_sha": "abc123",
  "changed_files": [
    "app/main.py",
    "requirements.txt",
    "infra/main.tf",
    ".github/workflows/ci.yml"
  ],
  "source_snapshot": {
    "app/main.py": "import subprocess\nsubprocess.call(user_input, shell=True)\n",
    "requirements.txt": "django==2.2.0\nrequests==2.19.0\n",
    "infra/main.tf": "resource \"aws_s3_bucket\" \"logs\" { acl = \"public-read\" }\n"
  }
}
```

## Optional Ollama

The backend works without Ollama. To enable LLM reasoning:

```bash
set OLLAMA_ENABLED=true
set OLLAMA_MODEL=llama3.1
```

Make sure Ollama is running at:

```text
http://localhost:11434
```

## Key Technical Challenges and Solutions

### Hallucinations and Wrong Risk Scores

- Used structured Pydantic schemas for findings and summaries.
- Added deterministic fallback scoring when Ollama is unavailable.
- Returned confidence scores and routed uncertain/high-risk findings to review.

### Agent Coordination and Failure Handling

- Added retry logic with exponential backoff for each subagent call.
- Used graceful degradation so the orchestrator continues if one agent fails.
- Added timeout handling to prevent one slow scan from blocking the full pipeline.

### Alert Fatigue from False Positives

- Added a deduplication layer to remove identical findings across agents before scoring.
- Tuned risk score thresholds so only priority findings surface for human review.

### Pipeline Latency

- Parallelized subagents with `asyncio.gather()` so all scanner agents run simultaneously.

## Outcomes

| Metric | Result |
| --- | --- |
| Detection Coverage | Vulnerability, misconfiguration, and compliance checks in one automated backend |
| False Positive Control | Deduplication, confidence tracking, and deterministic risk routing |
| Pipeline Speed | Parallelized agents reduce runtime compared with sequential scans |
| Human Review | Critical and High findings are routed to the review queue |

## Technology Stack

| Category | Tools and Technologies |
| --- | --- |
| API Backend | Python, FastAPI, Pydantic |
| Agents | asyncio, scanner classes, retry handling |
| AI Reasoning | Optional Ollama API |
| Security Automation | Vulnerability, misconfiguration, and compliance rules |
