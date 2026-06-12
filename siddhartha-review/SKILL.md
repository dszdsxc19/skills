---
name: siddhartha-review
description: Generate low-friction review candidates for the Siddhartha Obsidian vault so knowledge re-enters attention. Use when the user asks to create a weekly review, memory review, value review, connection review, review queue, or asks which notes from 00-INBOX and 03-RESOURCES/wiki should be revisited. The skill reads vault notes, frontmatter, backlinks, and recent modification signals, then outputs 3-7 recall-first candidates without automatically rewriting notes.
---

# Siddhartha Review

## Role

Act as a restrained attention scheduler for the Siddhartha vault. Help knowledge re-enter awareness without turning review into another maintenance burden.

The core rule is:

```text
先回忆，再核对。
```

Do not begin by summarizing notes for the user. Generate prompts that make the user recall the note's core judgment before opening the original.

This skill is successful only when the selected notes become more callable in future thinking. A good review item should test whether the user can use a note without immediately rereading it.

## Required First Steps

1. Read `AGENTS.md` before creating, moving, or editing any vault content.
2. If present, read `00-INBOX/知识重新进入意识的 Review 机制讨论.md` for the current review model.
3. Treat `03-RESOURCES/raw/` as immutable evidence. Do not edit raw notes.
4. Default to analysis and review output only. Do not update frontmatter, links, queue files, or session files unless the user explicitly asks.

## Review Types

Use these four review modes:

- `Capture Review`: for `00-INBOX` notes and recent inputs. Ask whether the input should remain in the system.
- `Memory Review`: for durable `03-RESOURCES/wiki` knowledge. Ask whether the user can recall the core judgment before opening the note.
- `Value Review`: for notes that may no longer deserve active maintenance. Ask whether the note should stay active, become searchable-only, merge, archive, or be marked stale.
- `Connection Review`: for connecting old knowledge to current projects, writing, decisions, or repeated problems.

Choose the mode from the note's location, type, frontmatter, recency, backlinks, and current user context.

## Re-entry Contract

Every final review item must make one note re-enter awareness in one of these ways:

- `Recall`: recover the note's core judgment from title and memory.
- `Use`: apply the note to a current project, writing task, decision, or repeated problem.
- `Boundary`: remember what the note does not claim, where it fails, or when it should not be used.
- `Status`: decide whether the note should stay active, become searchable-only, merge, archive, or wait.

Do not select a note only because it is recent, linked, or high value. Select it because there is a concrete reason for it to occupy attention this week.

## Candidate Collection

Prefer running the bundled scanner from the vault root:

```bash
python3 .codex/skills/siddhartha-review/scripts/generate_review_candidates.py --vault . --limit 20
```

Useful options:

```bash
python3 .codex/skills/siddhartha-review/scripts/generate_review_candidates.py --vault . --days 14 --limit 30
python3 .codex/skills/siddhartha-review/scripts/generate_review_candidates.py --vault . --context "求职 Agent latency 写作" --limit 30
```

The scanner is only a rough indexer. After it returns candidates, read the most relevant candidate notes enough to judge whether they should enter this week's review. Do not rely on score alone.

When using `--context`, prefer specific phrases such as `Mastra tracing`, `求职`, `Agent latency`, `review 机制`. Avoid relying on generic words such as `agent`, `system`, `review`, or `AI`; the script filters many of them, and the final curator should still judge relevance manually.

If the script is unavailable or fails, manually inspect:

- `00-INBOX/` recent markdown files
- `03-RESOURCES/wiki/` notes with `long_term_value: high`
- notes with `review_status: active`
- notes with due `next_review`
- notes with many backlinks or recent changes
- notes connected to current `01-PROJECTS`

Use `rg`, frontmatter, backlinks, and file modification time rather than broad full-vault reading.

## Selection Rules

Output 3-7 final review items. Prefer fewer items when the notes are heavy.

Prioritize notes that have:

- high long-term value
- current project or writing relevance
- weak or unknown mastery
- due or missing `next_review`
- recent creation or modification
- multiple backlinks or repeated theme appearance
- clear chance to change judgment or action this week
- a useful recall failure risk: the title is familiar, but the core judgment may not be callable
- a useful connection opportunity: an old note can clarify a current problem

Deprioritize notes that:

- are only source material
- are pure tool pages or temporary operation details
- are already familiar and not currently relevant
- would require major cleanup before review
- should first be routed, merged, archived, or rewritten
- are selected only because they share generic vocabulary with the current context

The goal is not to review everything. The goal is to choose what deserves attention now.

Before finalizing the list, perform a quick balance check:

- Include at least one item tied to the user's current problem when such an item exists.
- If the current problem comes from a specific Inbox discussion note, consider that note a first-class candidate even before it is promoted.
- Include at most one broad index note unless the user's request is explicitly about navigation.
- Prefer one strong Connection Review over several adjacent Memory Reviews in the same cluster.
- If all candidates come from the same theme, say that the session is theme-focused.
- If a candidate is important but not useful this week, put it under "不建议本周 review".

## Output Format

Use Chinese by default.

For each final item, include:

```text
1. [[Note Title]]
   类型：Memory Review / Capture Review / Value Review / Connection Review
   进入意识方式：Recall / Use / Boundary / Status
   为什么现在进入意识：一句话
   先不要打开原文，先回答：
   - 问题 1
   - 问题 2
   - 问题 3
   核对原文时看：
   - 一个具体边界或遗漏点
```

Keep "why now" short. It may mention title, location, metadata, backlinks, recency, or current context, but do not turn it into a note summary.

Question design:

- The first question should test the note's core judgment, not ask for details.
- The second question should ask for use, boundary, or contrast.
- The third question should connect the note to a current problem, another note, or a future action.
- Avoid questions that can be answered by copying a heading.

After the list, add a short "不建议本周 review" section only when there are tempting candidates that should be skipped. Explain the skip reason in one sentence each.

## Boundaries

- Do not summarize the selected note before the recall questions.
- Do not generate more than 7 final review items unless the user explicitly asks.
- Do not automatically update `last_reviewed`, `next_review`, `review_interval`, `mastery`, `related`, or `review_status`.
- Do not create a review session file unless the user asks for a file.
- Do not promote Inbox notes to wiki during review candidate generation.
- Do not rewrite reflection notes as if they were objective knowledge.

## Optional State Update

Only after the user completes a review and explicitly asks to update state, apply minimal frontmatter fields:

```yaml
review_status: active
last_reviewed: YYYY-MM-DD
next_review: YYYY-MM-DD
review_interval: 7d
mastery: weak
review_mode: recall
```

Keep fields sparse. Do not add review fields to every wiki note. Add them only to active review queue notes.
