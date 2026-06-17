---
name: vscode-worktree-workflow
description: Use this skill when the user wants to organize multi-repository development with VS Code multi-root workspaces and Git worktrees, especially for TypeScript full-stack projects, multiple repos in one feature, parallel feature work, branch isolation, or avoiding frequent stash/switch cycles. This skill should trigger for requests about "VS Code Workspace + Git Worktree", "multi-root workspace", "one feature across multiple repos", "multiple requirements in parallel", or "how should I structure worktrees".
---

# VS Code Workspace + Git Worktree Workflow

Use this skill to design and execute a multi-repository, multi-feature local development workflow.

Core model:

```txt
one feature/request = one VS Code workspace
one repo branch for that feature = one Git worktree
```

## When to Use Workspace Only

Recommend VS Code multi-root workspace without worktrees when all of these are true:

- The user is working on only one feature at a time.
- The user does not need the same repo checked out on multiple branches simultaneously.
- Switching branches inside the base repo is acceptable.

Example layout:

```txt
company-fullstack.code-workspace
├── crm-web
├── crm-api
└── crm-shared
```

In this case, tell the user to switch branches inside each repo normally:

```bash
cd crm-web
git switch feature/user-level

cd ../crm-api
git switch feature/user-level

cd ../crm-shared
git switch feature/user-level
```

## When to Use Workspace + Worktree

Recommend VS Code workspace plus Git worktrees when any of these are true:

- One feature changes multiple repositories.
- Multiple features or fixes are developed in parallel.
- Different features need different branches in the same repository.
- The user wants to avoid stashing, branch switching, and restarting project state.

Explain the key constraint clearly:

```txt
VS Code workspace records folders and settings.
It does not record Git branch state.
If two workspaces point to the same physical repo directory, they share the same branch.
Use worktrees to give each feature its own physical directory.
```

## Recommended Layout

Use this default structure unless the user already has a convention:

```txt
~/work/company/
├── base/
│   ├── crm-web/
│   ├── crm-api/
│   └── crm-shared/
│
├── worktrees/
│   ├── user-level/
│   │   ├── crm-web/
│   │   ├── crm-api/
│   │   └── crm-shared/
│   │
│   └── payment-check/
│       ├── crm-web/
│       ├── crm-api/
│       └── crm-shared/
│
└── workspaces/
    ├── user-level.code-workspace
    └── payment-check.code-workspace
```

Directory roles:

- `base/`: normal cloned repositories.
- `worktrees/`: per-feature branch working directories.
- `workspaces/`: VS Code `.code-workspace` files.

## Information to Collect

Before generating exact commands, identify:

- Organization root path, such as `~/work/company`.
- Feature/request slug, such as `user-level`.
- Repositories involved, such as `crm-web`, `crm-api`, `crm-shared`.
- Branch name for each repo, usually `feature/<feature-slug>`.
- Base branch, usually `origin/main` or `origin/master`.
- Whether each feature branch already exists remotely.

If the user does not provide these details, make conservative placeholders and state what should be replaced.

## Initialize Base Repositories

If the base repositories do not exist yet, create the base directory and clone them:

```bash
mkdir -p ~/work/company/base
cd ~/work/company/base

git clone git@github.com:company/crm-web.git
git clone git@github.com:company/crm-api.git
git clone git@github.com:company/crm-shared.git
```

## Create Worktrees for a New Feature Branch

Use this pattern when the feature branch does not exist yet:

```bash
mkdir -p ~/work/company/worktrees/user-level

cd ~/work/company/base/crm-web
git fetch
git worktree add ../../worktrees/user-level/crm-web -b feature/user-level origin/main

cd ~/work/company/base/crm-api
git fetch
git worktree add ../../worktrees/user-level/crm-api -b feature/user-level origin/main

cd ~/work/company/base/crm-shared
git fetch
git worktree add ../../worktrees/user-level/crm-shared -b feature/user-level origin/main
```

Adapt repo names, feature slug, branch names, and base branch to the user's project.

## Create Worktrees for Existing Remote Branches

If `origin/feature/user-level` already exists, prefer creating a local tracking branch first, then add the worktree:

```bash
cd ~/work/company/base/crm-web
git fetch
git switch -c feature/user-level origin/feature/user-level
git switch main
git worktree add ../../worktrees/user-level/crm-web feature/user-level
```

Avoid leaving daily development worktrees in detached HEAD. Do not recommend this as the default:

```bash
git worktree add ../../worktrees/user-level/crm-web origin/feature/user-level
```

Use it only for read-only inspection.

## Create the VS Code Workspace

Create `~/work/company/workspaces/user-level.code-workspace`:

```json
{
  "folders": [
    {
      "name": "web",
      "path": "../worktrees/user-level/crm-web"
    },
    {
      "name": "api",
      "path": "../worktrees/user-level/crm-api"
    },
    {
      "name": "shared",
      "path": "../worktrees/user-level/crm-shared"
    }
  ],
  "settings": {
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll.eslint": "explicit",
      "source.organizeImports": "explicit"
    },
    "search.exclude": {
      "**/node_modules": true,
      "**/dist": true,
      "**/.next": true,
      "**/coverage": true
    }
  }
}
```

Open it:

```bash
code ~/work/company/workspaces/user-level.code-workspace
```

## Development Routine

After opening the workspace, recommend separate named terminals:

```txt
web dev
api dev
shared watch
git
```

Example commands:

```bash
cd ~/work/company/worktrees/user-level/crm-web
pnpm dev
```

```bash
cd ~/work/company/worktrees/user-level/crm-api
pnpm dev
```

```bash
cd ~/work/company/worktrees/user-level/crm-shared
pnpm build --watch
```

## Common Worktree Commands

List worktrees:

```bash
git worktree list
```

Create a worktree with a new branch:

```bash
git worktree add <new-directory> -b <new-branch> <start-point>
```

Create a worktree with an existing local branch:

```bash
git worktree add <new-directory> <existing-branch>
```

Remove a worktree:

```bash
git worktree remove <worktree-directory>
```

Clean stale records after manual deletion:

```bash
git worktree prune
```

## Important Constraints

Git usually prevents the same local branch from being checked out by multiple worktrees at the same time.

If the user needs two working directories based on the same remote branch, create different local branches:

```bash
git worktree add ../crm-web-user-level-test -b feature/user-level-test origin/feature/user-level
```

Prefer `git worktree remove <path>` over manually deleting worktree directories. If the directory was already deleted manually, run:

```bash
git worktree prune
```

## Cleanup After a Feature Is Done

Before cleanup, confirm every involved repo has:

- committed changes,
- pushed branches,
- merged PR/MR if applicable,
- no uncommitted work that should be kept.

Then remove worktrees:

```bash
cd ~/work/company/base/crm-web
git worktree remove ../../worktrees/user-level/crm-web

cd ~/work/company/base/crm-api
git worktree remove ../../worktrees/user-level/crm-api

cd ~/work/company/base/crm-shared
git worktree remove ../../worktrees/user-level/crm-shared
```

Remove the workspace file and empty feature directory if appropriate:

```bash
rm ~/work/company/workspaces/user-level.code-workspace
rmdir ~/work/company/worktrees/user-level
```

Prune stale metadata:

```bash
git worktree prune
```

## Naming Conventions

Use short, readable slugs:

```txt
user-level
payment-check
bugfix-login
```

Use branch prefixes that match the work type:

```txt
feature/user-level
feature/payment-check
fix/login
```

Use matching workspace and worktree paths:

```txt
worktrees/user-level/crm-web
workspaces/user-level.code-workspace
```

## Response Pattern

When helping the user apply this workflow, return:

1. A short recommendation: workspace only, or workspace plus worktrees.
2. The target directory layout.
3. The exact shell commands for each repo.
4. The `.code-workspace` JSON.
5. Cleanup or caveats only when relevant.

Keep explanations concise. The user mainly needs correct paths, branch isolation rules, and commands they can run.
