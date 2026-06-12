---
name: siddhartha-inbox-triage
description: Triage 00-INBOX notes in the Siddhartha Obsidian vault. Use when the user asks to organize Inbox, decide whether captured notes should be kept, merged, promoted to wiki, moved to a project or area, archived, deleted, or asks for high-value Inbox candidates and next actions. The skill reads AGENTS.md, respects raw note immutability, and outputs restrained routing judgments without rewriting notes by default.
---

# Siddhartha Inbox Triage

## Role

Act as a restrained intake editor for the Siddhartha vault. Decide what each Inbox note is for before deciding where it should go.

The core rule is:

```text
先找锚点，再决定去向。
```

Do not summarize every Inbox note. Do not promote material to `03-RESOURCES/wiki` just because it looks useful. The output should help the user decide the next maintenance action with minimal cognitive load.

## Required First Steps

1. Read `AGENTS.md` before creating, moving, or editing any vault content.
2. Treat `03-RESOURCES/raw/` as immutable evidence. Do not edit raw notes.
3. Default to analysis only. Do not move, rename, rewrite, archive, delete, or update frontmatter unless the user explicitly asks.
4. Ignore `01-PROJECTS/blog-publishing/articles/` unless the user explicitly asks about publishing.

## Candidate Collection

Prefer running the bundled scanner from the vault root:

```bash
python3 .codex/skills/siddhartha-inbox-triage/scripts/scan_inbox.py --vault . --limit 30
```

Useful options:

```bash
python3 .codex/skills/siddhartha-inbox-triage/scripts/scan_inbox.py --vault . --days 21 --limit 40
python3 .codex/skills/siddhartha-inbox-triage/scripts/scan_inbox.py --vault . --context "Mastra source reading" --limit 30
```

The scanner is only a routing index. After it returns candidates, read the most relevant notes enough to judge their anchor, evidence, and likely next action.

If the scanner is unavailable, manually inspect:

- `00-INBOX/` notes with `long_term_value: high`
- recently modified Inbox notes
- Inbox clusters with repeated titles or folders
- notes that already link to wiki, project, or area pages
- notes whose `type` conflicts with their location or content

## Triage Actions

Use one of these actions for each final candidate:

- `Promote to Wiki`: the note has a stable, reusable, decontextualized judgment that meets the `knowledge` quality bar.
- `Convert Literature`: the note is source-derived and should become a faithful `literature` note or remain source material until the user's trigger point is clear.
- `Move to Project`: the note mainly serves a finite project, decision, interview, trip, article, or deliverable.
- `Move to Area`: the note supports an ongoing responsibility, practice, tool index, or life/work domain.
- `Merge`: the note overlaps with an existing wiki, project, area note, or sibling Inbox note.
- `Keep in Inbox`: the anchor or use is still unclear, but the material may be worth one more pass.
- `Archive or Drop`: the value is temporary, low, duplicated, or no longer worth maintenance.

Do not invent a new top-level directory. If the target is unclear, keep the note in `00-INBOX`.

## Judgment Questions

For every candidate, answer these before recommending action:

1. `锚点`: What concrete question, judgment, project, or recurring problem makes this note worth attention?
2. `证据`: Is the factual basis/source clear enough for the proposed destination?
3. `边界`: Is this input, literature, project material, area material, or stable knowledge?
4. `复用`: Will future reuse exceed the cost of recording, maintaining, and rereading it?
5. `相邻`: Which existing note or index would it connect to, merge into, or challenge?

If the anchor is weak, say so and choose `Keep in Inbox` or `Archive or Drop`.

## Output Format

Use Chinese by default. Output 5-10 candidates unless the user asks for a broader audit.

```text
## Inbox Triage

1. [[Note Title]]
   建议动作：Promote to Wiki / Convert Literature / Move to Project / Move to Area / Merge / Keep in Inbox / Archive or Drop
   锚点：一句话
   判断依据：
   - ...
   建议去向：路径或目标笔记；不确定则写 `00-INBOX`
   下一步：一个最小动作
   需要用户判断：一个问题
```

After the list, add a short section:

```text
## 不建议现在处理

- [[Note Title]]：一句话说明为什么跳过。
```

## Boundaries

- Do not write the note body during triage.
- Do not turn personal reflection into objective `knowledge`.
- Do not preserve AI output merely because it is articulate.
- Do not make a complete summary when a routing judgment is enough.
- Do not add review metadata during triage; use `siddhartha-review` for review queue work.
