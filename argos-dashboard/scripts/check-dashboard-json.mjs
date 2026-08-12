#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";

const file = process.argv[2];
if (!file) {
  console.error("Usage: node check-dashboard-json.mjs /absolute/path/to/dashboard.json");
  process.exit(2);
}

let dashboard;
try {
  dashboard = JSON.parse(fs.readFileSync(file, "utf8"));
} catch (error) {
  console.error(`Invalid JSON: ${error.message}`);
  process.exit(1);
}

const children = dashboard?.data?.dashboard?.root?.children;
if (!Array.isArray(children)) {
  console.error("Invalid Argos export: data.dashboard.root.children is not an array");
  process.exit(1);
}

const errors = [];
const warnings = [];
const ids = new Map();
const panels = [];

function rememberId(id, location) {
  if (!id) {
    warnings.push(`${location}: missing id`);
    return;
  }
  if (ids.has(id)) errors.push(`duplicate id ${id}: ${ids.get(id)} and ${location}`);
  else ids.set(id, location);
}

function validGridPos(pos) {
  return pos && ["x", "y", "w", "h"].every((key) => Number.isFinite(pos[key]));
}

function sameGridPos(a, b) {
  return ["x", "y", "w", "h"].every((key) => a[key] === b[key]);
}

children.forEach((child, index) => {
  const chart = child?.element?.props?.chart;
  const label = chart?.title || child?.id || `panel[${index}]`;
  const outer = child?.gridPos;
  const inner = chart?.gridPos;
  const pos = validGridPos(outer) ? outer : inner;

  rememberId(child?.id, `${label} container`);
  rememberId(chart?.id, `${label} chart`);
  for (const [queryIndex, query] of (chart?.queries || []).entries()) {
    rememberId(query?.key, `${label} query[${queryIndex}]`);
  }

  if (!chart) errors.push(`${label}: missing element.props.chart`);
  if (!chart?.title) warnings.push(`${label}: missing chart title`);
  if (!Array.isArray(chart?.queries) || chart.queries.length === 0) {
    warnings.push(`${label}: no chart queries`);
  }
  if (!validGridPos(pos)) {
    errors.push(`${label}: missing numeric gridPos x/y/w/h`);
    return;
  }
  if (validGridPos(outer) && validGridPos(inner) && !sameGridPos(outer, inner)) {
    errors.push(`${label}: container and chart gridPos differ`);
  }
  if (pos.x < 0 || pos.y < 0 || pos.w <= 0 || pos.h <= 0 || pos.x + pos.w > 24) {
    errors.push(`${label}: invalid 24-column geometry ${JSON.stringify(pos)}`);
  }

  panels.push({index, label, type: chart?.type || "unknown", ...pos});
});

for (let i = 0; i < panels.length; i += 1) {
  for (let j = i + 1; j < panels.length; j += 1) {
    const a = panels[i];
    const b = panels[j];
    const overlaps = a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
    if (overlaps) errors.push(`overlap: ${a.label} and ${b.label}`);
  }
}

const byType = panels.reduce((counts, panel) => {
  counts[panel.type] = (counts[panel.type] || 0) + 1;
  return counts;
}, {});
const rows = panels.length ? Math.max(...panels.map((panel) => panel.y + panel.h)) : 0;

console.log(`${path.basename(file)}: ${panels.length} panels, ${rows} grid rows`);
console.log(`Types: ${Object.entries(byType).map(([type, count]) => `${type}=${count}`).join(", ") || "none"}`);
if (warnings.length) {
  console.log("Warnings:");
  for (const warning of warnings) console.log(`- ${warning}`);
}
if (errors.length) {
  console.error("Errors:");
  for (const error of errors) console.error(`- ${error}`);
  process.exit(1);
}
console.log("OK: Argos structure, IDs, and 24-column layout passed checks");
