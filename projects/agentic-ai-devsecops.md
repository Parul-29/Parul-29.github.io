# Agentic AI System for DevSecOps Pipeline Automation

Architecture and Technical Overview  
Parul Inamdar

## Project Overview

This project is a multi-agent AI system built to automate security enforcement across CI/CD pipelines. When a developer pushes code to GitHub, specialized agents automatically scan for vulnerabilities, misconfigurations, and compliance violations.

A central reasoning agent powered by the Ollama API consolidates findings, assigns risk scores, generates fix suggestions, and escalates only critical issues to a human reviewer.

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
Performs multi-step reasoning, risk scoring, fix suggestions, and action routing
        |
        v
Decision and Output Layer
GitHub PR comments | AWS CloudWatch logs | Human review queue
```

## Component Breakdown

| Component | Technology | Responsibility |
| --- | --- | --- |
| Trigger Layer | GitHub Actions | Fires on every push or pull request |
| Orchestrator Agent | Python, Ollama API | Coordinates subagents and manages workflow state |
| Vulnerability Scanner | Bandit, Trivy, OWASP | Detects CVEs, dependency issues, and code flaws |
| Misconfiguration Scanner | Custom rules, AWS SDK | Checks Terraform, IAM policies, and S3 configurations |
| Compliance Checker | CIS Benchmarks engine | Validates against security standards and policies |
| Reasoning Agent | Ollama API, tool calling | Prioritizes risk, scores findings, and generates fixes |
| Human-in-the-Loop | GitHub PR flags, review queue | Escalates Critical and High findings for review |
| Logging and Monitoring | AWS CloudWatch | Tracks structured logs and false positive rates |

## Key Technical Challenges and Solutions

### Hallucinations and Wrong Risk Scores

- Used structured JSON output with Pydantic schema validation so model output must conform or retry.
- Added few-shot examples in the system prompt showing correct and incorrect risk reasoning.
- Returned a confidence score with every finding and auto-escalated uncertain outputs.

### Agent Coordination and Failure Handling

- Added retry logic with exponential backoff for each subagent call.
- Used graceful degradation so the orchestrator continues if one agent fails.
- Added timeout handling to prevent one slow scan from blocking the full pipeline.

### Alert Fatigue from False Positives

- Added a deduplication layer to remove identical findings across agents before scoring.
- Tuned risk score thresholds so only top findings surface as High or Critical.
- Tracked weekly false positive rate in CloudWatch, reducing it from about 35% to under 10%.

### Pipeline Latency

- Parallelized subagents with `asyncio.gather()` so all three scanner agents run simultaneously.
- Reduced runtime by about 60% compared with sequential execution.

## Outcomes

| Metric | Result |
| --- | --- |
| Detection Coverage | Vulnerability, misconfiguration, and compliance checks in one automated pipeline |
| False Positive Rate | Reduced from about 35% to under 10% through prompt tuning and output validation |
| Pipeline Speed | Parallelized agents cut runtime by about 60% compared with sequential execution |
| Human Review | Only Critical and High findings escalated; Low and Medium findings handled automatically |

## Technology Stack

| Category | Tools and Technologies |
| --- | --- |
| AI and Agents | Ollama API, tool calling, multi-step reasoning, asyncio |
| Security Tools | Bandit, Trivy, OWASP, CIS Benchmarks |
| Infrastructure | GitHub Actions, AWS EC2, CloudWatch, IAM |
| Backend | Python, FastAPI, Pydantic, psycopg2 |
