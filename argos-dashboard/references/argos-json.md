# Argos dashboard JSON notes

## Format boundary

Argos exports a private dashboard model. It resembles Grafana conceptually, but it is not Grafana-compatible.

Typical Argos exports contain:

```json
{
  "version": "...",
  "from": "...",
  "data": {
    "meta": {},
    "dashboard": {
      "id": "...",
      "root": {
        "id": "...",
        "attrs": {},
        "children": []
      }
    }
  }
}
```

Each child commonly contains a container `id`, `gridPos`, and an `element`. A chart element commonly stores configuration under `element.props.chart`, including its own `id`, `title`, `type`, `gridPos`, `queries`, aggregation, legend, units, and display options.

Grafana instead commonly uses fields such as `panels`, `gridPos`, `targets`, `datasource`, and `fieldConfig`. Similar concepts do not imply compatible fields or query semantics.

## Safe transformation rules

1. Use the current dashboard export as the authoritative schema sample.
2. Preserve unknown fields. Re-serialize the full parsed object rather than rebuilding it from a small hand-written schema.
3. Keep both copies of `gridPos` identical when a child and its chart each have one.
4. Treat the grid as 24 columns unless the export or UI provides contrary evidence. Require `x >= 0`, `w > 0`, and `x + w <= 24`.
5. Preserve working `queries` objects. Query families may contain service SLI, metrics, Bosun, log metrics, or other provider-specific subtrees.
6. Clone only from a working panel with the same query family. Change the smallest supported fields.
7. Generate unique IDs for every cloned container, chart, and query.
8. Use `null` only where the exported schema already uses or accepts it. Do not remove unknown fields merely because they look empty.
9. Validate JSON structure and geometry before import.

## Common presentation edits

Safe edits are export-dependent but usually include:

- `gridPos.x`, `gridPos.y`, `gridPos.w`, `gridPos.h`
- chart `title`
- chart `type`, such as compact Stat versus time series
- aggregation used for a Stat value
- aliases and legend placement
- decimals, percent/unit flags, and axis visibility

When changing visualization type, compare against an exported working panel of the target type. A Stat panel may require different aggregation and display fields from a graph panel.

## Import verification

After import and reload, verify:

- dashboard and panel count
- visible titles
- site, region, resource account, and time range
- query observable objects and aliases
- units and aggregation
- layout at multiple scroll positions
- panels with data versus panels showing no data

An accepted import is not proof of a correct dashboard. The rendered, reloaded state is the final authority.
