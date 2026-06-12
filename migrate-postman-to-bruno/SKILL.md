---
name: migrate-postman-to-bruno
description: Migrate every collection and request from the currently logged-in Postman desktop workspace into native Bruno collections, preserving folders, headers, bodies, scripts, tests, auth, and a Postman JSON backup. Use when the user asks to move, replace, copy, export, or bulk-import Postman requests into Bruno, especially when Postman has no convenient local export file or Bruno displays 0 requests after importing OpenCollection YAML.
---

# Migrate Postman To Bruno

Migrate the active Postman desktop workspace through Postman's authenticated local session and write native Bruno files.

## Preconditions

- Require macOS, Node.js 22 or newer, Postman desktop, and Bruno.
- Keep Postman logged in with the intended workspace active. The script opens Postman automatically when needed.
- Do not print Postman access tokens or request secrets.
- Do not delete Postman data or uninstall Postman.

## Run

Use the bundled launcher:

```bash
"$HOME/.codex/skills/migrate-postman-to-bruno/scripts/run.sh"
```

The default output is:

```text
~/Desktop/API/Postman Migrated
```

Specify another output location when needed:

```bash
"$HOME/.codex/skills/migrate-postman-to-bruno/scripts/run.sh" \
  --output "/absolute/path/to/Postman Migrated"
```

Skip reopening Bruno with:

```bash
"$HOME/.codex/skills/migrate-postman-to-bruno/scripts/run.sh" --no-open
```

## What The Script Does

1. Read Postman's `DevToolsActivePort`.
2. Connect to the Postman page through Chrome DevTools Protocol.
3. Read the current Postman access token and active workspace from IndexedDB without printing them.
4. Call Postman's authenticated Bifrost endpoints with `x-access-token`.
5. Fetch all collections and their complete sync trees.
6. Rebuild standard Postman Collection v2.1 JSON.
7. Convert through Bruno's official `@usebruno/converters`.
8. Write native Bruno files:
   - `bruno.json`
   - `collection.bru`
   - one `.bru` file per request
   - `folder.bru` for folders
9. Save source-compatible JSON under `_postman-json-backup`.
10. Parse every generated request with `@usebruno/filestore`.
11. Fail if generated request count differs from Postman's request count.
12. Add the migrated collection paths to Bruno's recent collections and reopen Bruno.

If the output directory already exists, rename it to a timestamped backup before migration.

## Verification

Report:

- Output directory
- Backup directory, when created
- Collection count
- Request count
- Folder count
- Any collection skipped or failed

Verify these conditions before declaring success:

```bash
find "$HOME/Desktop/API/Postman Migrated" \
  -name '*.bru' ! -name 'collection.bru' ! -name 'folder.bru' | wc -l
```

The count must equal `requestCount` in the script output.

Do not treat a collection containing only `opencollection.yml` as migrated. Bruno may recognize the collection shell while showing `0 requests`. Native per-request `.bru` files are required.

## Security

Postman requests may contain live Cookie, Authorization, API key, or bearer token values. Preserve them for a complete migration, but warn the user before committing the generated directory to Git. Never echo secret values in the final response.

## Troubleshooting

- `DevToolsActivePort` unavailable: the script opens Postman and waits up to 30 seconds; open it manually if startup is blocked.
- No page target: activate or reopen Postman, then rerun.
- `401` or `403`: do not use Bearer auth against the public Postman API. The script must use the internal Bifrost endpoint with `x-access-token`.
- Bruno shows `0 requests`: confirm the collection contains individual `.bru` files, then close and reopen Bruno.
- Network reset: rerun; the script retries transient fetch failures.
