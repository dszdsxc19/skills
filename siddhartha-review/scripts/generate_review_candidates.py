#!/usr/bin/env python3
"""Generate rough review candidates for the Siddhartha vault.

This script is an indexer, not the final curator. It reads lightweight metadata,
recent modification times, and wikilink backlink counts, then prints markdown
for Codex to inspect before choosing the final 3-7 review items.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import re
from pathlib import Path


WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)")
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
CONTEXT_STOPWORDS = {
    "agent",
    "agents",
    "ai",
    "llm",
    "system",
    "systems",
    "review",
    "skill",
    "skills",
    "知识",
    "系统",
    "机制",
    "复习",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vault", default=".", help="Vault root path")
    parser.add_argument("--days", type=int, default=7, help="Recent change window")
    parser.add_argument("--limit", type=int, default=20, help="Maximum candidates to print")
    parser.add_argument("--context", default="", help="Optional current project/topic words")
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
            key = key.strip()
            value = value.strip()
            current_key = key
            if value:
                data[key] = value.strip('"').strip("'")
            else:
                data[key] = []
        elif current_key and line.strip().startswith("- "):
            value = line.strip()[2:].strip().strip('"').strip("'")
            existing = data.setdefault(current_key, [])
            if isinstance(existing, list):
                existing.append(value)
    return data


def parse_date(value: object) -> dt.date | None:
    if not isinstance(value, str) or not value:
        return None
    patterns = (
        ("%Y-%m-%d %H:%M:%S", 19),
        ("%Y-%m-%d", 10),
        ("%Y/%m/%d", 10),
    )
    for fmt, size in patterns:
        try:
            return dt.datetime.strptime(value[:size], fmt).date()
        except ValueError:
            pass
    return None


def title_for(path: Path, text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem


def iter_markdown(root: Path) -> list[Path]:
    ignored_parts = {".git", ".obsidian", "node_modules"}
    files: list[Path] = []
    for path in root.rglob("*.md"):
        if ignored_parts.intersection(path.parts):
            continue
        files.append(path)
    return files


def note_kind(rel: str, fm: dict[str, object]) -> str:
    if rel.startswith("00-INBOX/"):
        return "Capture Review"
    if fm.get("review_status") == "active":
        return "Memory Review"
    if rel.startswith("03-RESOURCES/wiki/"):
        return "Memory Review"
    return "Connection Review"


def split_context_words(context: str) -> tuple[list[str], list[str]]:
    raw_words = [word for word in re.split(r"[\s,，、/]+", context.strip()) if word]
    kept: list[str] = []
    ignored: list[str] = []
    for word in raw_words:
        normalized = word.casefold()
        if normalized in CONTEXT_STOPWORDS:
            ignored.append(word)
            continue
        if len(normalized) < 2:
            ignored.append(word)
            continue
        kept.append(word)
    return kept, ignored


def context_hits(text: str, context_words: list[str]) -> tuple[int, list[str]]:
    lowered = text.lower()
    matched = [word for word in context_words if word and word.lower() in lowered]
    return len(matched), matched


def score_note(
    rel: str,
    text: str,
    fm: dict[str, object],
    backlinks: int,
    mtime: dt.datetime,
    now: dt.datetime,
    recent_days: int,
    context_words: list[str],
) -> tuple[int, list[str]]:
    score = 0
    reasons: list[str] = []

    long_term_value = str(fm.get("long_term_value", "")).lower()
    if long_term_value == "high":
        score += 30
        reasons.append("long_term_value=high")
    elif long_term_value == "medium":
        score += 12
        reasons.append("long_term_value=medium")

    if fm.get("review_status") == "active":
        score += 25
        reasons.append("review_status=active")

    next_review = parse_date(fm.get("next_review"))
    today = now.date()
    if next_review and next_review <= today:
        score += 35
        reasons.append(f"next_review due {next_review.isoformat()}")
    elif not next_review and rel.startswith("03-RESOURCES/wiki/"):
        score += 8
        reasons.append("wiki without next_review")

    mastery = str(fm.get("mastery", "")).lower()
    if mastery in {"weak", "unknown"}:
        score += 12
        reasons.append(f"mastery={mastery}")

    age_days = (now - mtime).days
    if age_days <= recent_days:
        score += 18
        reasons.append(f"modified {age_days}d ago")
    elif age_days >= 30 and rel.startswith("03-RESOURCES/wiki/"):
        score += 7
        reasons.append(f"not touched {age_days}d")

    if backlinks:
        backlink_score = min(backlinks * 3, 18)
        score += backlink_score
        reasons.append(f"{backlinks} backlinks")

    path_hits, path_context = context_hits(rel, context_words)
    body_hits, body_context = context_hits(text[:4000], context_words)
    if path_hits:
        score += path_hits * 18
        reasons.append(f"context_path={','.join(path_context[:3])}")
        if rel.startswith("00-INBOX/"):
            score += 10
            reasons.append("current inbox thread")
    if body_hits:
        score += body_hits * 8
        reasons.append(f"context_body={','.join(body_context[:3])}")

    if rel.startswith("03-RESOURCES/raw/"):
        score -= 100
        reasons.append("raw source skipped")
    if "04-ARCHIVES/" in rel:
        score -= 40
        reasons.append("archived")

    return score, reasons


def main() -> int:
    args = parse_args()
    root = Path(args.vault).expanduser().resolve()
    now = dt.datetime.now()
    context_words, ignored_context_words = split_context_words(args.context)

    all_md = iter_markdown(root)
    backlink_counts: dict[str, int] = {}
    note_texts: dict[Path, str] = {}

    for path in all_md:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        note_texts[path] = text
        for target in WIKILINK_RE.findall(text):
            backlink_counts[target.strip()] = backlink_counts.get(target.strip(), 0) + 1

    candidates = []
    for path, text in note_texts.items():
        rel = path.relative_to(root).as_posix()
        if not (rel.startswith("00-INBOX/") or rel.startswith("03-RESOURCES/wiki/")):
            continue
        if rel.startswith("03-RESOURCES/raw/"):
            continue

        fm = parse_frontmatter(text)
        title = title_for(path, text)
        backlinks = backlink_counts.get(title, 0) + backlink_counts.get(path.stem, 0)
        mtime = dt.datetime.fromtimestamp(os.path.getmtime(path))
        score, reasons = score_note(rel, text, fm, backlinks, mtime, now, args.days, context_words)
        if score <= 0:
            continue
        candidates.append(
            {
                "score": score,
                "title": title,
                "rel": rel,
                "kind": note_kind(rel, fm),
                "type": fm.get("type", ""),
                "long_term_value": fm.get("long_term_value", ""),
                "mtime": mtime,
                "reasons": reasons[:5],
            }
        )

    candidates.sort(key=lambda item: (-int(item["score"]), str(item["rel"])))

    print("# Review Candidate Index")
    print()
    print(f"- vault: `{root}`")
    print(f"- generated: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"- context: `{args.context}`" if args.context else "- context: none")
    if ignored_context_words:
        print(f"- ignored_context_words: `{', '.join(ignored_context_words)}`")
    print()

    for i, item in enumerate(candidates[: args.limit], start=1):
        print(f"## {i}. [[{item['title']}]]")
        print()
        print(f"- path: `{item['rel']}`")
        print(f"- suggested_mode: {item['kind']}")
        print(f"- score: {item['score']}")
        if item["type"]:
            print(f"- type: {item['type']}")
        if item["long_term_value"]:
            print(f"- long_term_value: {item['long_term_value']}")
        print(f"- modified: {item['mtime'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"- signals: {', '.join(item['reasons'])}")
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
