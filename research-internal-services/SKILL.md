---
name: research-internal-services
description: Investigate one or more ByteDance internal services and produce an evidence-backed technical research report and minimal implementation plan. Use for internal capability discovery, current-state audits, critical-path analysis, architecture, performance, reliability, observability, cost or metering research, integration assessment, gap analysis, and reuse-first technical proposals, especially when the result should be delivered as a native Feishu document. Default to read-only analysis unless the user explicitly requests implementation. Do not use for a single bug, direct feature implementation, generic framework education, or ordinary code review.
---

# Internal Service Research

Answer one decision-relevant question with evidence. Prefer existing internal platforms, SDKs, middleware, data, and proven service examples over designing a new system.

For a single failure or regression, use a diagnosis workflow. For direct implementation, first finish the decision boundary and acceptance criteria, then switch to the relevant development workflow.

## Establish the contract

Identify:

- target services, repositories, modules, versions, and environments;
- the single primary question the report must answer;
- included scope, explicit non-goals, and whether the task is research-only or includes implementation;
- required evidence sources and delivery destination.

State assumptions. Ask only when a missing choice would materially change the investigation. Treat ambiguous requests such as “看看” as read-only diagnosis and planning.

Do not edit code, configuration, infrastructure, dashboards, or production systems unless the user explicitly asks for that change. Read-only logs, traces, metrics, and internal documentation are in scope when available.

## Run a two-pass investigation

### 1. Map before deep-diving

Read applicable `AGENTS.md` files and repository guidance. Map service boundaries, entry points, dependencies, deployment identifiers, data stores, RPC or HTTP clients, model calls, storage, queues, configuration, existing observability, and relevant tests.

Search internal sources for existing platforms, SDKs, APIs, middleware, examples, dashboards, data tables, metrics, and standards. Prefer `bytedcli` and the relevant Feishu skills for ByteDance internal information. Use public or vendor documentation only to explain external technology; never use it as evidence of ByteDance's current internal state.

Read only the relevant section of [topic-lenses.md](references/topic-lenses.md); do not load every topic checklist into every investigation.

Trace one to three decision-critical request or resource paths end to end. Record the correlation keys, ownership boundaries, usage signals, failure boundaries, and evidence available at each hop.

### 2. Deepen only material gaps

Create an evidence matrix before more research. Deepen only uncertainties that could change the recommendation, priority, or implementation boundary. For a high-impact conclusion, two complementary evidence types are normally enough; for a scoped ordinary conclusion, one direct source is normally enough. Stop when the core answer and top three findings are stable, or when the remaining uncertainty requires unavailable access, production data, or an owner decision.

Do not continue searching merely to fill a predetermined long checklist. Do not recommend DDD, a new queue, cache, platform, abstraction, or independent data layer without a demonstrated gap.

## Grade evidence and impact

Use these evidence grades consistently:

- **A — Confirmed:** target code, configuration, logs, metrics, traces, reproducible tests, or observed target-environment behavior directly supports the claim.
- **B — Supported:** internal or official documentation, examples, interviews, or related environments mutually support the claim, but the target environment has not been fully verified.
- **C — To verify:** a single clue, reasonable inference, or missing direct evidence. Never write this as fact.

Assign `EV-xx` identifiers to evidence used by important conclusions. Keep facts, risks, improvement opportunities, and open questions separate. Use P0–P3 only for impact and urgency; do not let priority substitute for evidence strength.

Never reproduce credentials, tokens, cookies, or secret values. Cite only safe locations and remediation actions when sensitive material is discovered.

## Build the recommendation

Express each gap as current state → target state, affected decision, evidence, and priority. Compare only real alternatives:

1. reuse existing capability directly;
2. reuse it with configuration, SDK or middleware integration, or small business-context additions;
3. extend or build an independent layer only when the first two cannot meet the required granularity or behavior.

Recommend the smallest reversible option that establishes useful capability. Include success criteria, validation, rollback, ownership, dependencies, and explicit non-goals. Distinguish service-level cost or health from end-to-end business attribution when both matter, and avoid double counting.

## Deliver the report

Use [report-structure.md](references/report-structure.md) to select sections. Required outputs are:

- direct answer and recommended action;
- scope and method;
- current capability map and one to three critical paths;
- evidence-graded gaps;
- recommended minimum change with verification and rollback;
- risks, open questions, and evidence index.

Include solution comparison only when at least two real choices exist. Include a diagram only when it materially clarifies a multi-component path or architecture.

When the user requests Feishu delivery, read and follow the `lark-doc` and `lark-drive` skills, then use [feishu-template.md](references/feishu-template.md). Copy the canonical template before editing; never overwrite the template itself. Return the verified Feishu link and a short conclusion summary.

Keep temporary research artifacts under `work/` or another non-repository scratch location and remove them after use. Do not leave research notes in the target repository unless the user requests a repository artifact.

Use subagents only when the user explicitly permits them or another applicable instruction requires them. Partition independent evidence lanes, then independently verify their claims before including them.
