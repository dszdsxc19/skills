#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ ! -d "$SCRIPT_DIR/node_modules/@usebruno/converters" ]] ||
   [[ ! -d "$SCRIPT_DIR/node_modules/@usebruno/filestore" ]]; then
  npm ci --prefix "$SCRIPT_DIR"
fi

exec node "$SCRIPT_DIR/migrate.js" "$@"
