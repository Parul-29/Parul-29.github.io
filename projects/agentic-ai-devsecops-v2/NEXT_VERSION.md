# Next Version of the Agentic AI DevSecOps Project

## Current foundation

The current system already provides an end-to-end automated security workflow:

- GitHub Actions sends repository scan requests on pushes, pull requests, and
  manual workflow runs.
- A FastAPI service on Vercel orchestrates vulnerability, misconfiguration, and
  compliance agents in parallel.
- Supabase persists scan results and the human-review queue.
- Gemini can produce a structured executive summary while deterministic
  reasoning remains available as a fallback.
- Focused unit tests protect the GitHub Actions permissions rule and prevent a
  Tekton YAML false positive.

The next version should make the results more accurate, actionable, reliable,
and easier to operate in a real engineering workflow.

## 1. Improve scan quality

### Broader and more accurate detection

- Add secrets detection for API keys, private keys, tokens, and credentials.
- Add software-composition analysis using an advisory source such as OSV for
  real dependency vulnerability matching instead of a small fixed version list.
- Add stronger Terraform, IAM, Dockerfile, Kubernetes, and GitHub Actions
  checks using parsers where practical instead of only regular expressions.
- Attach precise line numbers, evidence, and remediation references to every
  finding.

### Reduce false positives

- Add path-aware rules so each scanner processes only relevant file types and
  directories.
- Support a repository-level `.devsecops.yml` file for ignored paths, approved
  exceptions, enabled rules, and risk thresholds.
- Add finding fingerprints so the same issue is deduplicated across commits.
- Let users mark findings as false positives with a reason and expiry date.

## 2. Make scans useful in pull-request workflows

- Scan only files changed in a push or pull request rather than uploading a
  broad repository snapshot on every run.
- Publish results as GitHub Check Runs, pull-request annotations, or summary
  comments.
- Define policy gates, such as blocking a merge only for new critical findings.
- Compare each scan with the prior commit to show new, resolved, and recurring
  findings.
- Add issue-tracker integration for human-review findings that need ownership.

## 3. Add a finding lifecycle

- Extend persisted data with statuses such as `open`, `acknowledged`,
  `resolved`, `false_positive`, and `accepted_risk`.
- Store assignee, due date, resolution notes, and audit timestamps.
- Add repository, branch, severity, status, and date filters to API queries.
- Add pagination and ordering to scan-history and review-queue endpoints.

## 4. Strengthen reliability and observability

- Move long-running scans to a durable job queue or worker so completion does
  not depend on a Vercel serverless invocation remaining active.
- Add idempotency keys and safe retry handling for GitHub delivery retries.
- Record structured logs, scan duration, agent failures, Gemini latency,
  deterministic-fallback rate, and scan volume.
- Add health/readiness checks for Supabase and optional Gemini availability.
- Expand tests with API, Supabase integration, Gemini fallback, and end-to-end
  GitHub Actions coverage.

## 5. Production safeguards

- Add authenticated API access and GitHub webhook signature verification.
- Apply rate limits and request-size limits to protect the scan endpoint.
- Keep Supabase service-role credentials server-side only and apply appropriate
  database access policies.
- Define retention rules for source snapshots and scan records so sensitive
  source data is not stored longer than necessary.

## 6. User experience and reporting

- Build a small dashboard after the API and data model support filtering and
  lifecycle status.
- Show severity trends, open-review items, scan history, and time-to-resolution.
- Export reports for audit or portfolio demonstrations.
- Add clear README diagrams and example API responses for faster onboarding.

## Suggested delivery order

1. Improve rule coverage, path awareness, and false-positive handling.
2. Add changed-file scanning and GitHub pull-request feedback.
3. Implement a finding lifecycle with paginated history APIs.
4. Add durable job processing, monitoring, and broader automated tests.
5. Add production safeguards and a dashboard built on the mature API.

## Success metrics

- **Scan reliability:** percentage of scan requests that complete successfully
  without manual retry.
- **Detection quality:** number of validated high-severity findings and the
  false-positive rate by rule.
- **Developer impact:** percentage of pull requests receiving feedback before
  merge and time to resolve high-risk findings.
- **Performance:** median scan duration, agent execution time, and API latency.
- **AI quality:** Gemini success rate, deterministic-fallback rate, and summary
  usefulness feedback from reviewers.
- **Operational scale:** number of repositories and scans supported per day
  within the target cost budget.
