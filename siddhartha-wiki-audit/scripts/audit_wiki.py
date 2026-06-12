#!/usr/bin/env python3
"""Audit Siddhartha wiki metadata and structural risks.

This script is read-only. It produces issue candidates for Codex to inspect.
"""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import re
from pathlib import Path


FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)")
VALID_TYPES = {"literature", "knowledge", "reflection", "project"}
INDEX_WORDS = ("索引", "index", "moc", "toc")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vault", default=".", help="Vault root path")
    parser.add_argument("--focus", default="", help="Optional focus: ai, metadata, links, review")
    parser.add_argument("--limit", type=int, default=120, help="Maximum issues to print")
    return parser.parse_args()


def parse_frontmatter(text: str) -> dict[str, object]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}

    data: dict[str, object] = {}
    current_key: str | None = None
    for raw_line in match.group(1).splitlines():
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if not line.startswith(" ") and ":" in line:
            key, value = line.split(":", 1)
            current_key = key.strip()
            value = value.strip()
            data[current_key] = value.strip('"').strip("'") if value else []
        elif current_key and line.strip().startswith("- "):
            existing = data.setdefault(current_key, [])
            if isinstance(existing, list):
                existing.append(line.strip()[2:].strip().strip('"').strip("'"))
    return data


def title_for(path: Path, text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem


def is_empty(value: object) -> bool:
    return value is None or value == "" or value == []


def note_records(root: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    wiki = root / "03-RESOURCES" / "wiki"
    if not wiki.exists():
        return records
    for path in sorted(wiki.rglob("*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = path.relative_to(root).as_posix()
        records.append(
            {
                "path": path,
                "rel": rel,
                "text": text,
                "fm": parse_frontmatter(text),
                "title": title_for(path, text),
            }
        )
    return records


def backlink_counts(root: Path, titles: set[str]) -> dict[str, int]:
    counts = {title: 0 for title in titles}
    ignored_parts = {".git", ".obsidian", "03-RESOURCES/raw"}
    for path in root.rglob("*.md"):
        rel = path.relative_to(root).as_posix()
        if any(part in rel for part in ignored_parts):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for link in WIKILINK_RE.findall(text):
            title = Path(link).name
            if title in counts:
                counts[title] += 1
    return counts


def add_issue(
    issues: list[tuple[str, str, str, str, str]],
    severity: str,
    rel: str,
    title: str,
    problem: str,
    recommendation: str,
) -> None:
    issues.append((severity, rel, title, problem, recommendation))


def audit_record(
    record: dict[str, object],
    backlinks: int,
    issues: list[tuple[str, str, str, str, str]],
) -> None:
    rel = str(record["rel"])
    title = str(record["title"])
    text = str(record["text"])
    fm = record["fm"]
    assert isinstance(fm, dict)

    note_type = str(fm.get("type", "")).lower()
    ltv = str(fm.get("long_term_value", "")).lower()
    source = fm.get("source")
    related = fm.get("related")
    is_index = any(word in title.casefold() for word in INDEX_WORDS)

    if not fm:
        add_issue(issues, "P1", rel, title, "missing frontmatter", "add required Siddhartha metadata before further wiki maintenance")
        return

    for field in ("created", "type", "classification", "classification_basis", "long_term_value", "long_term_value_basis", "related"):
        if is_empty(fm.get(field)):
            sev = "P2" if field in {"classification_basis", "long_term_value_basis", "related"} else "P1"
            add_issue(issues, sev, rel, title, f"missing or empty `{field}`", f"fill `{field}` with explicit basis or route the note out of wiki")

    if note_type and note_type not in VALID_TYPES:
        add_issue(issues, "P1", rel, title, f"invalid type `{note_type}`", "use literature / knowledge / reflection / project")

    if note_type == "literature" and is_empty(source):
        add_issue(issues, "P1", rel, title, "literature note has empty source", "add the source or demote until provenance is clear")

    if note_type == "reflection":
        add_issue(issues, "P1", rel, title, "reflection appears in wiki", "move to an Area unless it has been converted into stable knowledge")

    if note_type == "project":
        add_issue(issues, "P2", rel, title, "project note appears in wiki", "move to the relevant project or rewrite as decontextualized knowledge")

    if isinstance(source, str) and "01-PROJECTS/blog-publishing/articles" in source:
        add_issue(issues, "P2", rel, title, "source points at publishing copy", "point source to the original note, manifest, or external source")

    if ltv == "high" and not is_empty(related) and backlinks < 2:
        add_issue(issues, "P2", rel, title, "high-value note is weakly connected", "add 1-3 meaningful related links or merge into a stronger index")

    if ltv == "high" and "AI/" in rel and is_empty(fm.get("review_status")) and backlinks >= 8:
        add_issue(issues, "P3", rel, title, "high-link AI note has no active review status", "consider for a small review queue only if it should be actively recalled")

    lower = text[:6000].casefold()
    body_without_links = WIKILINK_RE.sub("", lower)
    if not is_index and note_type == "knowledge" and any(marker in body_without_links for marker in ("速记", "讲座", "访谈", "文章来源", "原文")) and is_empty(source):
        add_issue(issues, "P2", rel, title, "knowledge note may be source-bound but lacks provenance", "check whether it should be literature or needs source evidence")

    if is_index:
        links = WIKILINK_RE.findall(text)
        if len(links) > 35:
            add_issue(issues, "P2", rel, title, "index has many links and may be overbroad", "split by entry question or separate stable knowledge from cases")


def duplicate_candidates(records: list[dict[str, object]]) -> list[tuple[str, list[str]]]:
    buckets: dict[str, list[str]] = collections.defaultdict(list)
    for record in records:
        title = str(record["title"])
        rel = str(record["rel"])
        tokens = re.findall(r"[A-Za-z0-9]+|[\u4e00-\u9fff]{2,}", title.casefold())
        key_tokens = [token for token in tokens if token not in {"ai", "llm", "agent", "工程", "索引", "机制"}]
        key = " ".join(key_tokens[:3])
        if key:
            buckets[key].append(rel)
    return [(key, paths) for key, paths in buckets.items() if len(paths) >= 2]


def main() -> int:
    args = parse_args()
    root = Path(args.vault).expanduser().resolve()
    records = note_records(root)
    titles = {str(record["title"]) for record in records}
    backlinks = backlink_counts(root, titles)
    issues: list[tuple[str, str, str, str, str]] = []

    for record in records:
        rel = str(record["rel"])
        if args.focus and args.focus.casefold() == "ai" and "/AI/" not in rel:
            continue
        audit_record(record, backlinks.get(str(record["title"]), 0), issues)

    if not args.focus or args.focus.casefold() in {"ai", "links", "duplicates"}:
        for key, paths in duplicate_candidates(records):
            if args.focus.casefold() == "ai" and not any("/AI/" in path for path in paths):
                continue
            issues.append(
                (
                    "P3",
                    ", ".join(paths[:4]),
                    key,
                    "possible overlapping titles or concepts",
                    "inspect whether these should be linked, merged, or separated by clearer questions",
                )
            )

    severity_order = {"P1": 0, "P2": 1, "P3": 2}
    issues.sort(key=lambda item: (severity_order.get(item[0], 9), item[1], item[3]))

    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("# Wiki Audit Candidate Index\n")
    print(f"- vault: `{root}`")
    print(f"- generated: {now}")
    if args.focus:
        print(f"- focus: {args.focus}")
    print(f"- wiki_notes: {len(records)}")
    print(f"- issues_printed: {min(len(issues), args.limit)} / {len(issues)}")
    print()

    for index, (severity, rel, title, problem, recommendation) in enumerate(issues[: args.limit], 1):
        print(f"## {index}. {severity} - {title}")
        print()
        print(f"- file: `{rel}`")
        print(f"- problem: {problem}")
        print(f"- recommendation: {recommendation}")
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
