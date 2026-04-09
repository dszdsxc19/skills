# Repository Guidelines

## Project Structure & Module Organization
This repository stores reusable agent skills, not a single application. Each skill lives under `skills/<skill-name>/` and is typically centered on a `SKILL.md` entrypoint. Supporting materials sit beside it in subdirectories such as `templates/`, `references/`, `assets/`, `agents/`, `scripts/`, or `evals/`. Examples:

- `skills/harness-next/templates/` contains reusable document templates.
- `skills/skillshare/scripts/run.sh` contains the skillshare runner.
- `skills/changeset-helper/evals/` stores evaluation data.

Use [`README.md`](/Users/admin/Desktop/mine/skills/README.md) for the high-level repo purpose and `skills-lock.json` for pinned external skill sources.

## Build, Test, and Development Commands
There is no repo-wide build step. Work is mainly Markdown and shell-script editing.

- `bash skills/harness-check/scripts/check.sh <project-root>`: run the harness flow checker against another project.
- `sh skills/skillshare/scripts/run.sh <command>`: run the skillshare helper without installing it globally.
- `git status` and `git diff -- skills/<name>`: review only the skill you changed before committing.

If you add a new script, keep it runnable with standard `sh` or `bash` unless the skill explicitly requires another runtime.

## Coding Style & Naming Conventions
Prefer short, direct Markdown written as operational instructions. Keep headings descriptive and avoid long narrative sections. Use lowercase, hyphenated skill directory names such as `information-writing-strategy`. Shell scripts should start with a shebang, use portable quoting, and include brief usage comments near the top. Preserve existing indentation: Markdown lists use two-space continuation when needed, and shell scripts use two spaces or tabs consistently within the file being edited.

## Testing Guidelines
Testing here is mostly validation of instructions and scripts.

- Run the relevant script directly after editing it.
- Verify referenced paths exist, especially files under `templates/`, `references/`, and `assets/`.
- For workflow changes, test the documented command end to end and update examples if output or behavior changed.

Name new evaluation fixtures clearly, for example `evals/smoke.json` or `evals/regression.json`.

## Commit & Pull Request Guidelines
Recent history follows short Conventional Commit style messages such as `feat: update skill` and `feat: changeset-helper`. Continue using prefixes like `feat:`, `fix:`, `docs:`, or `chore:` with a concise scope.

Pull requests should explain which skill directories changed, why the change was needed, and how it was validated. Include command examples or before/after snippets when altering prompts, templates, or script behavior.
