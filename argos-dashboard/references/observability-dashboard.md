# High-quality observability dashboard design

## Design objective

Optimize for diagnosis, not metric inventory. The dashboard should make user impact and likely fault domain obvious before the reader scrolls deeply.

## Metric hierarchy

### User impact

- availability or success rate
- QPS/throughput
- P95/P99 latency, plus timeout rate when available
- error/failure QPS or rate

Use Stat panels for current state and sparklines. Pair them with time-series panels for shape and correlation.

### Service and runtime health

- CPU and memory utilization
- instance/container health and saturation
- event-loop lag, heap/external memory, goroutines, GC, thread pools, or connection pools only when production data is stable and interpretable

Prefer comparable panels with consistent aggregations, commonly P99 for resource hotspots and tail latency where appropriate.

### Dependencies

For each critical database, cache, storage, MQ, scheduler, and downstream service, prefer:

- traffic/QPS
- latency P95/P99
- failures/timeouts
- pool acquisition or backlog/saturation when available

Compare read and write paths in one panel when they share units and diagnostic meaning. Keep exact PSM aliases visible.

### Async and business completion

For asynchronous workflows, separate:

- request accepted
- queued or scheduled
- rejected or dropped
- background execution success/failure
- terminal completion and time-to-terminal
- consistency/reconciliation failures

Do not add these panels until the metrics are confirmed in production. Empty speculative panels create false confidence and noise.

## Dense 24-column layout pattern

Adapt the following pattern rather than forcing it:

| Row | Content | Typical geometry |
|---|---|---|
| 1 | 6–8 golden-signal Stat cards | `w=3–4`, `h=4` |
| 2 | 3–4 service resource trends | `w=6–8`, `h=6` |
| 3 | 2 service latency/error trends | `w=12`, `h=7` |
| 4 | 3 database/cache comparisons | `w=8`, `h=7` |
| 5 | 2 downstream or async trends | `w=12`, `h=7` |

Keep the first viewport dense but readable. Reserve full-width panels for timelines that genuinely require width, such as high-cardinality downstream comparisons or long async completion paths.

## Naming and consistency

- Put the short scope first: `Assets`, `Creative`, `MySQL Read / Write`.
- Put the metric second: `可用性`, `QPS`, `P99`, `失败 QPS`.
- Use the same term for the same concept across the dashboard.
- Keep aliases short but exact enough to distinguish read/write and upstream/downstream.
- Use matching colors, units, and aggregations for comparison panels.

## No-data policy

Classify an empty panel before deciding what to do:

1. Query/configuration error: fix it.
2. Metric exists but has no events in the selected window: widen the range and verify.
3. Metric is not instrumented or not emitted in production: record an observability gap.
4. Metric has no diagnostic value: remove it only when restructuring is authorized.

Never convert no-data to zero merely to make a panel look healthy.

## Acceptance checklist

- Top viewport answers health, traffic, tail latency, and major dependency state.
- At least one time-series view exists for every critical Stat family.
- Read/write or service comparisons use the same units and time range.
- No panel overlaps or extends beyond the grid.
- Panel titles fit without truncating the distinguishing scope.
- Empty panels have been explained or removed deliberately.
- The dashboard was reloaded after import and reviewed at top, middle, and bottom.
