#!/bin/bash
# Cloud sessions start from a fresh clone: fetch the submodules, install packages and build the
# generated assets, so `npm run dev` and `npm test` work. Without a licensed Helvetica the font step
# writes a stand-in (see scripts/build-fonts.mjs); lockups then show in a system sans.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-.}"

# The site imports from vendor/brandkit and vendor/json-url; fetch them only if missing.
if [ ! -f vendor/brandkit/package.json ] || [ ! -f vendor/json-url/package.json ]; then
  git submodule update --init --recursive --depth 1
fi

# Install and build only if this script or the package files changed since the last success,
# or if the generated assets are missing.
hashes=node_modules/.session-start.sha256
if ! sha256sum --check --status "$hashes" 2>/dev/null || [ ! -f src/fonts.css ] || [ ! -f public/capabilities.json ]; then
  rm -f "$hashes"
  npm ci --no-audit --no-fund
  npm run build:assets --silent
  sha256sum .claude/hooks/session-start.sh package.json package-lock.json > "$hashes"
fi
