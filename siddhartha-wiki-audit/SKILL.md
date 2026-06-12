---
name: siddhartha-wiki-audit
description: Audit 03-RESOURCES/wiki and related maintenance surfaces in the Siddhartha Obsidian vault. Use when the user asks to inspect wiki quality, AI topic structure, metadata completeness, source and related fields, duplicate or merge candidates, index drift, review metadata gaps, or structural risks in the knowledge base. The skill reports issues and recommendations without editing notes by default.
---

# Siddhartha Wiki Audit

## Role

Act as a structural auditor for the Siddhartha vault. Find places where the knowledge layer may be drifting away from the vault constitution.

The core rule is:

```text
只报告结构风险，不抢人类的知识路径判断。
```

This skill is for audit and recommendation. It should not rewrite wiki notes, regenerate MOCs, or fix links unless the user explicitly asks for a follow-up implementation.

## Required First Steps

1. Read `AGENTS.md` before creating, moving, or editing any vault content.
2. Treat `03-RESOURCES/raw/` as immutable evidence.
3. Exclude `01-PROJECTS/blog-publishing/articles/` from normal source-of-truth checks unless the user asks about publishing.
4. Default to read-only reporting.

## Audit Collection

Prefer running the bundled scanner from the vault root:

```bash
python3 .codex/skills/siddhartha-wiki-audit/scripts/audit_wiki.py --vault .
```

Useful options:

```bash
python3 .codex/skills/siddhartha-wiki-audit/scripts/audit_wiki.py --vault . --focus ai
python3 .codex/skills/siddhartha-wiki-audit/scripts/audit_wiki.py --vault . --limit 80
```

The scanner flags likely issues. After it runs, inspect the highest-impact notes manually before giving final recommendations.

## Audit Dimensions

Check these dimensions:

- `Metadata`: missing or suspicious `created`, `type`, `classification`, `classification_basis`, `long_term_value`, `long_term_value_basis`, `source`, or `related`.
- `Type Boundary`: `knowledge` that looks source-bound, `literature` without source, `reflection` in wiki, project material promoted too early.
- `Source Integrity`: notes with factual claims but no source or unclear source; source paths that point to publishing copies instead of originals.
- `Connection Health`: high-value wiki notes with `related: []`, index notes with weak reciprocal links, isolated notes in dense topics.
- `Index Drift`: MOC/index pages that duplicate each other, mix stable knowledge with event material, or grow too broad.
- `AI Topic Governance`: AI wiki pages that should be grouped by principle, engineering practice, product judgment, workflow, or source/case material.
- `Review Readiness`: high-value wiki notes without `review_status` only when they are truly worth active recall.
- `Merge Candidates`: notes with overlapping titles, repeated concepts, or multiple pages answering the same question.

## Severity

Use these levels:

- `P1`: likely violates the vault constitution or risks corrupting the knowledge layer.
- `P2`: creates retrieval, reuse, or maintenance friction.
- `P3`: cleanup opportunity; worth batching, not urgent.

## Output Format

Use Chinese by default. Lead with findings, not a generic summary.

```text
## Wiki Audit Findings

1. P1/P2/P3 - 问题标题
   文件：[[Note Title]] 或路径
   现象：一句话
   风险：一句话
   建议：一个最小修复动作
```

Then add:

```text
## 结构判断

- 当前最主要的结构风险：
- 不建议立刻做的事：
- 下一步最小动作：
```

For broad audits, keep findings to the top 10-15 issues and group low-severity items by pattern.

## Boundaries

- Do not rewrite a note during audit.
- Do not automatically create a TOC/MOC; ask the user for entry questions and ordering judgment first.
- Do not mark every high-value note for review. Active review is a small queue, not a global metadata requirement.
- Do not treat empty `source` as a defect for every `knowledge` note; prioritize source gaps where factual claims, literature notes, or migrated content need traceability.
- Do not treat `related: []` as a defect for every note; prioritize high-value and dense-topic notes.
