# ADR 0001: Deploy FastAPI on Vercel and persist scans in Supabase

- **Status:** Accepted
- **Date:** 2026-08-07

## Context

The project needs a publicly reachable API for GitHub Actions scan requests and
persistent storage for scan history, findings, timestamps, and review status.
The solution should be quick to deploy, simple to demonstrate, and require
minimal infrastructure management.

## Decision

Deploy the FastAPI backend as a Vercel Python serverless function and store
scan records in a Supabase PostgreSQL table through the Supabase REST API.

## Rationale

- Vercel provides a simple Git-based deployment workflow for the FastAPI API.
- Supabase provides managed PostgreSQL storage and a browser-based interface
  for inspecting scan results during demonstrations.
- The combination lets GitHub Actions trigger a scan without managing a custom
  server or database infrastructure.

## Consequences

### Positive

- Fast deployment and simple operational setup.
- Persistent scan history is available after serverless requests complete.
- The Supabase table makes scan results easy to verify and demonstrate.

### Trade-offs

- Vercel serverless functions are not ideal for durable, long-running
  background jobs.
- Storage queries need pagination and filtering as scan history grows.
- Service credentials must remain in environment variables and never be
  committed to the repository.

## Alternatives considered

- **In-memory storage:** rejected because scan history disappears between
  serverless invocations.
- **Self-managed VM and PostgreSQL:** offers more control but requires more
  deployment and operational effort.
- **Dedicated background worker and queue:** appropriate for a future version
  with longer scans and higher throughput.
