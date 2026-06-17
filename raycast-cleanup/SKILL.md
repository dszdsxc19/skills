---
name: raycast-cleanup
description: Audit and trim Raycast command clutter, identify low-value enabled commands and extensions, and provide safe UI paths for disabling commands. Use when the user asks to clean up Raycast, reduce enabled commands, disable AI Chat or Calculator, sync/export Raycast settings, or remember Raycast cleanup steps for future use.
---

# Raycast Cleanup

## Quick Rules

Use Raycast's own UI for disabling commands. Do not edit `raycast-enc.sqlite` or `raycast-activities-enc.sqlite`; they are encrypted app databases and direct edits can corrupt state or be overwritten.

Prefer disabling over deleting unless the user explicitly wants uninstalling. Disabled commands stop appearing in normal Raycast search and are easier to restore.

## Fast Disable Path

For one-off cleanup:

1. Open Raycast.
2. Search the exact command name, for example `AI Chat` or `Calculator`.
3. Select the command result.
4. Press `Command-Shift-D` to disable the selected command.
5. Repeat for each noisy command.

If the shortcut is unavailable, use the preferences path:

1. Open Raycast Preferences with `Command-,`, or run Raycast's `Settings` / `Preferences` command.
2. Go to `Extensions`.
3. Search for `AI Chat`, `Calculator`, or the extension name.
4. Toggle off the command, or disable/uninstall the extension if the whole extension is low-value.

Useful direct opens:

- `open raycast://extensions` opens the extensions area in Raycast.
- If UI automation is blocked with `osascript is not allowed assistive access`, tell the user to grant Accessibility permission or complete the toggle manually.

## Current User Preference

For this user's Raycast setup, the user explicitly wants these off:

- `AI Chat`
- `Calculator`

The prior audit found these likely keepers:

- `Search File`
- `My Schedule` / `Calendar`
- `Raycast Notes`
- `My Issues` / `GitHub`
- `Clipboard History` only if the user actively uses clipboard lookup

The prior audit found these low-value candidates:

- `Visual Studio Code`, unless Raycast is used to search/open VS Code projects.
- `Google Chrome`, unless Raycast is used for tabs, bookmarks, history, or profile switching.
- Empty extension directories under `~/Library/Application Support/com.raycast.macos/extensions`: `44949313-8a50-437e-9a9d-32134222efb3`, `a8d461aa-3521-46b6-8f42-4c561a8f8368`, `5c75261b-1853-4557-8e92-271c0dc6a9b1`.
- `Color Picker` if the user is not currently doing UI/design work.

## Audit Workflow

Use local read-only checks first:

```bash
find "$HOME/Library/Application Support/com.raycast.macos/extensions" -maxdepth 1 -mindepth 1 -type d -print
defaults read com.raycast.macos 2>/dev/null
find "$HOME/Library/Application Support/com.raycast.macos/extensions" -type f -maxdepth 5 -print -exec stat -f '%Sm %z bytes' -t '%Y-%m-%d %H:%M:%S' {} \;
```

Evidence to prioritize:

- Recent extension cache writes suggest recent use, but are not conclusive.
- Empty extension directories are strong disable/uninstall candidates.
- `command-extension_*` defaults only prove a command was opened or configured at least once.
- Raycast Wrapped summaries provide high-level activity only; PNG assets are usually not enough for command-level decisions.

## Sync and Backup

Use Raycast's built-in export/import or Cloud Sync rather than copying encrypted database files.

For portable backup:

1. Run Raycast's `Export Preferences & Data` command.
2. Save the `.rayconfig` file somewhere versioned or synced.
3. Import it on another Mac with Raycast's import command.

The exported `.rayconfig` is expected to cover app settings, Store extensions, aliases, hotkeys, snippets, quicklinks, script command folders, floating notes, and Raycast Notes. Some account-bound or external service state may still need login/reauthorization.

For automatic sync, use Raycast account/Cloud Sync if available in the installed plan. Verify in Raycast Preferences under Account or Cloud Sync before promising exact coverage.
