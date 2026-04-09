---
name: skill-manager
description: |
  Orchestrates the full lifecycle of AI skills. Use this skill whenever the user wants
  to manage skills end to end: find new skills, evaluate install options, install or
  uninstall skills, initialize skillshare, sync skills across AI CLIs, update tracked
  skills, recover from sync issues, create a new skill, or coordinate cross-device
  skill workflows. This skill is the routing layer for skill management requests:
  discovery should go through find-skills, creation should go through skill-creator,
  and installation/sync/update/uninstall/status/doctor/push/pull should go through
  skillshare.
---

# Skill Manager

Use this skill as the top-level router for skill management tasks. Do not duplicate the
full manuals of the underlying skills. Route the request, apply the right default, and
then rely on the specialized skill for detailed execution.

## Routing Rules

### 1. Discovery and evaluation

Use `find-skills` when the user wants to:

- search for a new skill
- ask whether a skill exists for a task
- compare candidate skills
- get installable addresses or package references

Workflow:

1. Clarify the task domain and what capability the user wants.
2. Delegate search and quality filtering to `find-skills`.
3. Return candidate install sources.
4. If the user wants to install one, switch to `skillshare` for the installation step.

Do not invent a separate search workflow when `find-skills` is a fit.

### 2. Creating a new skill

Use `skill-creator` when the user wants to:

- create a new skill from scratch
- turn an existing workflow into a reusable skill
- revise or improve an existing skill

Default creation target:

- global skillshare source: `~/.config/skillshare/skills/<skill-name>`

Only use another location when the user explicitly asks for it, for example:

- project-local `.skillshare/skills/<skill-name>`
- a repo-local skills folder outside skillshare management

Workflow:

1. Capture the skill intent, trigger conditions, output expectations, and validation plan.
2. Delegate the authoring workflow to `skill-creator`.
3. Create the skill in the default global skillshare source unless the user overrides it.
4. If the user wants the new skill distributed to tool targets, run `skillshare sync` after creation.

### 3. Install, update, sync, and operational management

Use `skillshare` when the user wants to:

- initialize skill management
- install a skill from a known source
- sync skills to Claude, Cursor, Windsurf, or other targets
- update tracked or installed skills
- uninstall a skill
- inspect status, diff, logs, or health
- restore from trash
- manage targets, include/exclude rules, or copy/symlink modes
- push or pull skills across devices

Treat `skillshare` as the system of record for lifecycle operations.

## Default Decisions

- Search first with `find-skills` when no install source is known.
- Create with `skill-creator` when the user needs a new custom skill.
- Execute lifecycle operations with `skillshare` once a concrete source or target action exists.
- Default to global skillshare mode unless the user explicitly asks for project mode.
- After `skillshare` mutations such as install, update, uninstall, collect, or target changes, include the required follow-up `skillshare sync` step unless the command already covers the final sync behavior.

## Non-Interactive Rule

AI callers should prefer non-interactive `skillshare` usage. When examples are needed, use
explicit flags instead of workflows that require prompts or TUI interaction.

Examples:

```bash
skillshare init --no-copy --all-targets --git --skill
skillshare install owner/repo -s my-skill
skillshare uninstall my-skill --force
skillshare sync
skillshare check --json
skillshare doctor
```

Do not re-document every `skillshare` flag here. If the task needs command-level detail,
consult the `skillshare` skill.

## Intent-to-Skill Map

| User intent | Primary skill |
|-------------|---------------|
| "Find a skill for X" | `find-skills` |
| "Create a new skill for X" | `skill-creator` |
| "Install this skill" | `skillshare` |
| "Set up skillshare" | `skillshare` |
| "Sync to my CLIs" | `skillshare` |
| "Update or remove a skill" | `skillshare` |
| "Recover, diagnose, compare, or push/pull skills" | `skillshare` |

## Boundaries

- Do not replace `find-skills` for discovery.
- Do not replace `skill-creator` for authoring.
- Do not replace `skillshare` for execution and sync.
- Do not default new skills into this repository's `skills/` directory unless the user explicitly requests that location.
