# ADR 0002: Use Gemini, Ollama, and deterministic fallback for reasoning

- **Status:** Accepted
- **Date:** 2026-08-07

## Context

Security scanner agents produce structured findings, but developers also need a
concise summary, prioritization, and recommended next steps. The system must be
usable in both deployed and local environments, and it must still return a
result when an LLM is unavailable.

## Decision

Use Gemini for structured reasoning in the deployed Vercel backend, support
Ollama for local development, and use deterministic scoring and summarization
as the fallback for either provider.

## Rationale

- Gemini provides cloud-hosted structured reasoning for the deployed workflow.
- Ollama allows local experimentation without depending on a cloud LLM.
- Deterministic scoring keeps severity routing and scan completion reliable
  when model credentials, connectivity, quota, or the model service fail.

## Consequences

### Positive

- The project supports both cloud and local AI-assisted reasoning.
- Results remain available even when Gemini or Ollama cannot respond.
- The `reasoning_provider` field makes the source of each summary explicit.

### Trade-offs

- LLM summaries add latency and may vary between requests.
- Gemini requires secure API-key management and has usage costs.
- The deterministic fallback is less nuanced than an LLM-generated summary.

## Alternatives considered

- **Gemini only:** rejected because local development and outage resilience
  would be weaker.
- **Ollama only:** rejected because a local model service is not practical for
  the deployed Vercel backend.
- **Deterministic rules only:** retained as a fallback, but does not provide
  the same natural-language prioritization and summary quality.
