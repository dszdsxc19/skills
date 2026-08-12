---
name: argos-dashboard
description: Create, restructure, and validate ByteDance Argos observability dashboards through the logged-in browser and Argos JSON import/export. Use when a user asks to create, optimize, compact, consolidate, migrate, or audit an Argos dashboard; add service, interface/Method, MySQL, resource, downstream, latency, traffic, availability, error, or SLI metrics; add endpoint-level filters and linked panels; or edit an exported Argos dashboard JSON file.
---

# Argos Dashboard

Build dense, decision-oriented Argos dashboards without guessing the private JSON schema or fabricating unavailable signals.

## Required operating model

1. Use the available Chrome/browser-control skill and the user's logged-in session for Argos. Read that skill before browser actions.
2. Treat a dashboard URL as the exact environment context. Preserve its site, region, resource account, time range, variables, and permissions unless the user asks to change them.
3. If the user asks only to inspect or advise, stay read-only. A request to create, edit, optimize, consolidate, or import a dashboard authorizes the corresponding dashboard mutation.
4. Export the current Argos JSON before structural edits. Save a working copy outside the skill directory and never overwrite the only export.
5. Treat the export as the schema authority. Argos JSON is not Grafana JSON. Never invent fields from Grafana conventions.

## Workflow

### 1. Establish scope and background

- Identify the target dashboard, primary services/PSMs, databases, regions, resource account, and desired time horizon.
- When background is missing, discover it from accessible internal service documentation, code, APM, existing dashboards, and dependency views. Prefer internal-service research tools when available.
- Write down the critical request paths and async paths before choosing metrics. Typical paths include RPC/HTTP entry, handler or middleware, cache/database, object or media storage, scheduler/audit, MQ, and terminal state.
- Distinguish stable production signals from proposed, empty, or unverified metrics.

### 2. Inventory the current dashboard

- Inspect dashboard variables, existing panels, query types, observable objects, aggregations, aliases, units, and grid positions.
- Record reusable panels whose queries are already known to work.
- Look for duplicated information, excessive full-width charts, inconsistent naming, mixed scopes, and empty panels.
- Export JSON and run:

```bash
node scripts/check-dashboard-json.mjs /absolute/path/to/export.json
```

Read [references/argos-json.md](references/argos-json.md) before changing the exported structure.

### 3. Design the metric hierarchy

Read [references/observability-dashboard.md](references/observability-dashboard.md) when selecting metrics or restructuring more than a few panels.

Order information by incident value:

1. User impact: availability/success rate, traffic, tail latency, errors or timeouts.
2. Service health: CPU, memory, saturation, runtime health, and instance/container state when reliable.
3. Critical dependencies: database/cache/storage/MQ/downstream QPS, latency, and failures.
4. Business or async completion: accepted, queued, rejected, terminal success/failure, consistency, and backlog when actually instrumented.
5. Change context: deployments, configuration changes, and alerts when supported.

Use a mix of compact Stat panels and time-series panels. Do not make every metric a distribution or a full-width graph.

### 3.5 Add interface-level drill-down when needed

Read [references/interface-filtering.md](references/interface-filtering.md) when the user asks to filter by interface, endpoint, RPC Method, or router.

- Discover live methods and validate per-method QPS, success rate, and P99 before creating a variable.
- Add a service-scoped Method variable with multi-select and `ALL` rather than duplicating one dashboard per interface.
- Link only request golden-signal panels to the Method variable. Keep CPU, memory, MySQL, and broad downstream panels service-scoped unless their queries genuinely expose the same interface dimension.
- Bind SLI panels with the verified `service.method` TagKvs filter; do not guess `method`, `_method`, or Grafana-style label syntax.
- Use average success rate for a selected time range. Never use maximum success rate because it can hide failures behind a 100% peak.
- Verify one real method and then return the dashboard to `ALL` for its default overview state.

### 4. Transform the exported JSON

- Parse and modify JSON structurally; never use regex replacement on serialized JSON.
- Preserve working query objects, dashboard metadata, variables, datasource semantics, IDs, units, region/account context, and query-specific fields unless the requested change requires otherwise.
- Change only the fields needed for layout and presentation, usually panel `gridPos`, chart `gridPos`, title, visualization type, aggregation, legend, decimals, and related display options.
- Keep container-level and chart-level `gridPos` synchronized when both exist.
- Give new panels unique container, chart, and query IDs. Do not duplicate identifiers.
- Prefer cloning a known-good panel with the same query family, then changing only the observable object/metric and presentation fields supported by that exported schema.
- Never represent missing data as zero. Retain an important empty reliability panel only when it exposes a real instrumentation gap, and report that gap explicitly.

Run the checker after every substantial transform. Resolve structural errors and overlaps before import.

### 5. Import and verify

1. Import the transformed JSON through Argos's **Import JSON** UI.
2. Confirm the import and wait for the dashboard to render.
3. Reload the dashboard; do not trust only the immediate post-import state.
4. Verify panel count, exact titles, query scopes, grid alignment, units, legends, non-empty data, and current time/region/account.
5. Inspect at least the top, middle, and bottom of the dashboard. Capture a screenshot when it materially helps review.
6. Report empty panels as observability gaps, not as healthy zeros.
7. Keep the finished dashboard tab as the deliverable when the browser-control surface supports tab finalization.
8. For interface-linked panels, verify the saved dashboard model as well as the rendered UI; editor previews can retain unsaved TagKvs changes.

## Quality bar

- A reader can answer within seconds: Is the service healthy? Who is affected? Is traffic abnormal? Is latency or error rate rising? Is the bottleneck local, database, or downstream?
- The first viewport contains the most important cross-service signals.
- Titles are short and scope-explicit, such as `Assets P99`, `Creative 可用性`, and `MySQL Read / Write · QPS`.
- Comparison panels use consistent aliases, units, aggregation, and time range.
- Every panel has a diagnostic purpose; remove decorative or redundant panels only when the user authorized restructuring.
- Stable golden signals take precedence over speculative business metrics.
- Final verification is evidence-based: reloaded UI, expected panel count, no overlaps, correct titles, and data/no-data state recorded.

## Guardrails

- Do not import Grafana dashboard JSON into Argos.
- Do not guess metric names, tags, or query schemas when an exported working example can be inspected.
- Do not silently change site, region, resource account, dashboard ID, or access control.
- Do not claim a metric is healthy when Argos shows no data.
- Do not stop after generating JSON; import and reload verification are required when the user asked for an actual dashboard change.
