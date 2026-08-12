# Argos interface and Method filtering

Use this workflow to let one Argos dashboard switch request golden signals between the whole service and individual RPC/HTTP interfaces.

## Contents

- [Scope and invariants](#scope-and-invariants)
- [Discover live interfaces first](#1-discover-live-interfaces-first)
- [Choose the variable source](#2-choose-the-variable-source)
- [Bind SLI panels in the UI](#3-bind-sli-panels-in-the-ui)
- [Use honest Stat aggregations](#4-use-honest-stat-aggregations)
- [Verify saved state](#5-verify-saved-state-not-only-preview-state)
- [Known pitfalls](#known-pitfalls)

## Scope and invariants

- Scope the variable to one service. Use names such as `assets_method` or `creative_method`, not a generic `method`, when a dashboard covers multiple PSMs.
- Link availability/success rate, QPS, error rate/QPS, and P95/P99 latency for that service.
- Do not link CPU, memory, MySQL, cache, or broad downstream panels unless the underlying query exposes the same interface tag with meaningful semantics.
- Keep `ALL` as the default so the dashboard opens as a service overview.
- Treat an empty variable value or an unverified tag query as a configuration problem, not as evidence that the service has no interfaces.

## 1. Discover live interfaces first

Prefer the APM service command because it returns the same per-Method golden signals used by Argos:

```bash
bytedcli --json apm service methods \
  --psm <service.psm> \
  --latency \
  --range 1h \
  --region <Argos-region>
```

Confirm that the result contains real methods and sensible `total_qps`, `success_rate`, and `latency_p99` values. Use APM **服务监控 → 接口 → Method** as a visual cross-check when needed.

## 2. Choose the variable source

### Prefer a dynamic Query only when previewed

Argos Query variables use the Metrics datasource and `tag_values(...)` syntax. Use a dynamic Query only when the raw Metrics measurement and its interface tag are known and the variable preview returns real methods.

Do not use an SLI display name such as `service.request.server.latency.total` in a Metrics `tag_values(...)` query unless the preview proves that it works. SLI-backed panels and Metrics variables are different query surfaces.

### Fall back to a Custom variable safely

When no verified raw Metrics tag query is available:

1. Create a **Custom** variable from the live methods returned by `bytedcli apm service methods`.
2. Name it `<scope>_method`.
3. Enable multi-select.
4. Enable the `ALL` option.
5. Describe exactly which panels it controls.
6. Report that newly deployed interfaces must be added later.

Do not fabricate a dynamic query merely to avoid this maintenance note.

## 3. Bind SLI panels in the UI

For each request golden-signal panel:

1. Open the panel menu and choose **编辑**.
2. Expand **TagKvs**.
3. Choose key `service.method`.
4. Keep function `literal_or`.
5. Set value to the variable reference, for example `$assets_method`.
6. Use it as a filter and turn **分组** off.
7. Click **添加** so the completed tag row appears above the blank input row.
8. Save the panel, then complete the separate **保存看板** change-description dialog before leaving the editor.

The saved SLI query contains the filter under `sli.tags`, not under `observable_object_tags`:

```json
{
  "key": "service.method",
  "value": "$assets_method",
  "is_filter": true,
  "function": "literal_or"
}
```

JSON casing depends on the surface. Browser exports commonly use camelCase fields, while `bytedcli --json apm argos dashboard get` returns normalized snake_case fields. Preserve the casing of the model being edited; do not mix both schemas.

## 4. Use honest Stat aggregations

- Success rate/availability over a selected range: use `Avg`. Never use `Max`; one healthy point can otherwise display 100% while failures occurred elsewhere in the range.
- QPS: choose `Current`, `Avg`, or `Max` deliberately and state the meaning in the title or description when ambiguity matters.
- P95/P99: use `Current` for the latest tail or `Max` for the worst tail spike. Keep the choice consistent across compared services.
- Error QPS/rate: use `Current`, `Avg`, or `Max` according to the incident question; never convert no-data to zero.

## 5. Verify saved state, not only preview state

Select one method with non-trivial traffic and verify all of the following:

1. The URL contains `var-<variable>=<method>` after the selector closes.
2. Linked success rate, QPS, and latency values change to the chosen method.
3. Unlinked resource, database, and unrelated service panels remain service-scoped.
4. Switching to `ALL` restores the service overview.
5. The dashboard was reloaded and still contains the variable and filters.

Use the dashboard model as a second authority:

```bash
bytedcli --json apm argos dashboard get \
  --id <dashboard-id> \
  --region <Argos-region> |
jq '{
  variables: .data.meta.variables,
  linked_panels: [
    .data.dashboard.root.children[]
    | select(any(.element.props.chart.queries[0].sli.tags[]?; .key == "service.method"))
    | {
        title: .element.props.chart.title,
        stat_aggr: .element.props.chart.aggr,
        tags: .element.props.chart.queries[0].sli.tags
      }
  ]
}'
```

Expect the variable to be multi-select with `include_all: true`, and expect every intended SLI panel to contain the `service.method` filter. A visible selector alone is not sufficient proof that panels are linked.

## Known pitfalls

- Closing or navigating back from the panel editor before completing **保存看板** can discard TagKvs changes even when the preview looked correct.
- A multi-select option may not apply until the selector closes; confirm the URL and refreshed panel values.
- `service.method` is the verified SLI tag for RPC Method filtering. HTTP route filtering may require a different verified tag such as `service.http_route`; inspect the panel's TagKvs options before using it.
- A single cross-service Method variable can select a method absent from another PSM. Prefer one variable per service unless both services intentionally share the same interface namespace.
