#!/usr/bin/env bash
# Deletes the 85 remote branches audited in research/repository/stale-branches-2026-11-16.md.
# Each is contained in main or claude/amazing-euler-nizzgr, or was squash-merged or superseded.
# The list keeps every tip SHA, so a branch can be restored: git push origin <sha>:refs/heads/<name>
set -euo pipefail
cd "$(dirname "$0")/.."
branches=$(sed -n '/^```$/,/^```$/p' research/repository/stale-branches-2026-11-16.md | grep -v '^```' | awk '{print $2}')
echo "Deleting $(echo "$branches" | wc -l | tr -d ' ') branches from origin…"
# shellcheck disable=SC2086
git push origin --delete $branches
