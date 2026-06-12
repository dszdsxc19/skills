#!/usr/bin/env python3
"""Scan Siddhartha Inbox notes and print rough triage candidates.

This script is read-only. It is a routing index, not the final decision maker.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
from pathlib import Path


FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)")
STOPWORDS = {"ai", "llm", "agent", "agents", "system", "系统", "知识", "笔记"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vault", default=".", help="Vault root path")
    parser.add_argument("--days", type=int, default=14, help="Recent modification window")
    parser.add_argument("--limit", type=int, default=30, help="Maximum notes to print")
    parser.add_argument("--context", default="", help="Optional current project or topic")
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


def split_context(context: str) -> list[str]:
    words = [word for word in re.split(r"[\s,，、/]+", context.casefold()) if word]
    return [word for word in words if len(word) >= 2 and word not in STOPWORDS]


def has_empty_list(value: object) -> bool:
    return value == [] or value == "" or value is None


def suggested_action(rel: str, fm: dict[str, object], text: str) -> tuple[str, list[str]]:
    note_type = str(fm.get("type", "")).lower()
    classification = str(fm.get("classification", "")).lower()
    long_term_value = str(fm.get("long_term_value", "")).lower()
    source = fm.get("source")
    related = fm.get("related")
    reasons: list[str] = []

    if long_term_value == "high":
        reasons.append("long_term_value=high")
    if note_type:
        reasons.append(f"type={note_type}")
    if classification:
        reasons.append(f"classification={classification}")

    lower_rel = rel.casefold()
    lower_text = text[:5000].casefold()

    if "mastra-source-reading" in lower_rel or "源码" in lower_text or "排查" in lower_text:
        return "Move to Project or Merge", reasons + ["appears tied to source-reading/project material"]

    if note_type == "literature":
        if has_empty_list(source):
            return "Convert Literature", reasons + ["literature needs source/evidence check"]
        return "Convert Literature or Merge", reasons + ["source-derived material"]

    if note_type == "reflection":
        return "Move to Area or Keep in Inbox", reasons + ["reflection should not be rewritten as objective knowledge"]

    if note_type == "project":
        return "Move to Project", reasons + ["project type in Inbox"]

    if long_term_value == "high" and note_type == "knowledge":
        if has_empty_list(related):
            return "Promote to Wiki or Merge", reasons + ["knowledge candidate lacks related links"]
        return "Promote to Wiki", reasons + ["stable knowledge candidate"]

    if long_term_value in {"low", ""}:
        return "Archive or Drop", reasons + ["weak long-term value signal"]

    return "Keep in Inbox", reasons + ["needs anchor check"]


def score_note(
    rel: str,
    text: str,
    fm: dict[str, object],
    mtime: dt.datetime,
    now: dt.datetime,
    recent_days: int,
    context_words: list[str],
    backlinks: int,
) -> tuple[int, list[str]]:
    score = 0
    signals: list[str] = []

    ltv = str(fm.get("long_term_value", "")).lower()
    if ltv == "high":
        score += 35
        signals.append("high value")
    elif ltv == "medium":
        score += 15
        signals.append("medium value")

    note_type = str(fm.get("type", "")).lower()
    if note_type in {"knowledge", "literature", "project"}:
        score += 8
        signals.append(f"type={note_type}")

    age_days = (now - mtime).days
    if age_days <= recent_days:
        score += 18
        signals.append(f"modified {age_days}d")

    if backlinks:
        score += min(backlinks * 4, 20)
        signals.append(f"{backlinks} backlinks")

    lowered = (rel + "\n" + text[:5000]).casefold()
    hits = [word for word in context_words if word in lowered]
    if hits:
        score += len(hits) * 18
        signals.append("context=" + ",".join(hits[:3]))

    if "apple notes 全量汇总" in rel.casefold():
        score -= 20
        signals.append("bulk import")

    return score, signals


def iter_notes(root: Path) -> list[tuple[Path, str, str, dict[str, object]]]:
    inbox = root / "00-INBOX"
    notes: list[tuple[Path, str, str, dict[str, object]]] = []
    if not inbox.exists():
        return notes
    for path in sorted(inbox.rglob("*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = path.relative_to(root).as_posix()
        notes.append((path, rel, text, parse_frontmatter(text)))
    return notes


def backlink_counts(root: Path, inbox_titles: set[str]) -> dict[str, int]:
    counts = {title: 0 for title in inbox_titles}
    ignored = {".git", ".obsidian", "03-RESOURCES/raw"}
    for path in root.rglob("*.md"):
        rel = path.relative_to(root).as_posix()
        if any(part in rel for part in ignored):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for link in WIKILINK_RE.findall(text):
            title = Path(link).name
            if title in counts:
                counts[title] += 1
    return counts


def main() -> int:
    args = parse_args()
    root = Path(args.vault).expanduser().resolve()
    now = dt.datetime.now()
    notes = iter_notes(root)
    titles = {title_for(path, text) for path, _, text, _ in notes}
    backlinks = backlink_counts(root, titles)
    context_words = split_context(args.context)

    rows = []
    for path, rel, text, fm in notes:
        title = title_for(path, text)
        score, signals = score_note(
            rel,
            text,
            fm,
            dt.datetime.fromtimestamp(path.stat().st_mtime),
            now,
            args.days,
            context_words,
            backlinks.get(title, 0),
        )
        action, reasons = suggested_action(rel, fm, text)
        rows.append((score, title, rel, action, signals, reasons))

    rows.sort(key=lambda item: (-item[0], item[2]))

    print("# Inbox Triage Candidate Index\n")
    print(f"- vault: `{root}`")
    print(f"- generated: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    if args.context:
        print(f"- context: {args.context}")
    print()

    for index, (score, title, rel, action, signals, reasons) in enumerate(rows[: args.limit], 1):
        print(f"## {index}. [[{title}]]")
        print()
        print(f"- path: `{rel}`")
        print(f"- rough_action: {action}")
        print(f"- score: {score}")
        if signals:
            print(f"- signals: {', '.join(signals)}")
        if reasons:
            print(f"- routing_reasons: {', '.join(reasons)}")
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
