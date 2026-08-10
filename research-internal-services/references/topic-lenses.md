# Topic lenses

Read only the section matching the primary question. These are prompts for evidence collection, not mandatory report sections.

## Architecture, performance, and reliability

- Map runtime, deployment, resource limits, concurrency, synchronous versus asynchronous work, and direct upstream/downstream dependencies.
- Trace database queries, transactions, indexes, connection pools, caching, queues, RPC/HTTP timeouts and retries, storage, and external services only when they appear on a critical path.
- Identify failure mode, trigger condition, blast radius, consistency or compensation behavior, and whether current tests or runtime evidence cover it.
- For growth questions, state the workload assumption and identify the first likely resource or dependency boundary; do not invent a capacity number without measurement.

## Observability and diagnostics

- Separate metrics, logs, traces, alerts, profiles, database observability, and AI/model/tool-call telemetry.
- Verify actual instrumentation, context propagation, exporters/backends, sampling, labels, retention, dashboards, and alert ownership. An installed dependency does not prove production reporting.
- Mark breaks in `request_id`, `log_id`, `trace_id`, `task_id`, or business context across every critical hop.
- Evaluate whether a user-visible failure or slow request can be traced to a root cause within the stated time window.

## Cost, metering, and attribution

- Keep estimation, metering, attribution, allocation, billing, and chargeback distinct.
- For each resource or model call, identify usage source, unit price source, existing cost, granularity, ownership, and correlation key.
- Separate each service's own cost from end-to-end business-task cost. Define rules that prevent shared or downstream cost from being counted twice.
- Verify whether existing ledgers, billing platforms, model gateways, traces, and business IDs can be joined before proposing new collection or storage.

## Integration and internal capability reuse

- For every internal capability, record the problem it solves, target-service integration state, runtime verification state, evidence, and reuse level.
- Use reuse levels: direct reuse, integration reuse, extension reuse, partial reuse, or not applicable.
- Distinguish “the company has this platform” from “the target service uses it” and “the target environment currently emits data.”
