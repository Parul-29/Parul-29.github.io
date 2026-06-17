# Chaos Engineering for Cloud-Native Resilience

## Topic

Systematic resilience validation through controlled failure experiments.

## Design Quality Connection

Traditional design quality practices such as code reviews and unit tests evaluate whether the implementation matches expected behavior. This research extends that idea with experimental validation: instead of only assuming a design is reliable, it tests whether the system continues to work under realistic failure conditions.

The goal is to make reliability measurable with real metrics such as recovery time, detection time, error rate, blast radius, and cascading failure behavior.

## Research Articles and Evidence

### Article 1: Chaos Engineering, Netflix, 2016

This article supports the methodology for systematic failure testing. Its key contribution is a validation framework for proving that resilience patterns work in production-like conditions.

Example: circuit breakers can prevent cascading failures when a downstream service becomes slow or unavailable.

### Article 2: Cloud Failure Study, Gunawi et al., 2016

This study provides empirical evidence from 597 real cloud outages. The key findings show that 44% of failures cascade and 60% of downtime is caused by slow detection.

Example: the data shows why observability is not just an operations feature, but a design requirement.

## Combined Framework

Together, the research provides a complete framework:

- Evidence: what commonly fails in cloud systems
- Method: how to test whether the design survives those failures

This connects outage data with practical chaos engineering experiments.

## Applications and Practical Use

### 1. Design Phase

Use a failure catalog to evaluate architecture decisions.

Example question: how does the design handle network partitions?

### 2. Development

Implement resilience patterns based on risk data.

Example: add circuit breakers to critical service paths where cascading failure risk is high.

### 3. Testing

Add chaos experiments to CI/CD pipelines so resilience is validated before production.

Example: automatically test service crash recovery, latency spikes, network partitions, health checks, and retry behavior.

## Bottom Line

This project moves reliability validation from "hoping systems work" to proving that they continue to work under stress.
