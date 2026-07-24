#!/usr/bin/env bash
# Update EVERY installed skills.sh skill to its latest upstream version — one command.
#
# The skills.sh CLI is the package manager for agent skills: it tracks each installed
# skill's source and syncs all of them across every harness on the machine. This wrapper
# just calls `npx skills update`. It does NOT touch:
#   - local skills authored in this repo (skills/<slug>/)  -> re-run `bash install.sh`
#   - the GSD framework                                    -> `bash scaffold/install-gsd.sh`
#
#   bash scaffold/update-skills.sh          # update all installed skills
#   bash scaffold/update-skills.sh --list   # just show what's installed, don't update
set -euo pipefail

if ! command -v npx >/dev/null 2>&1; then
  echo "error: npx (Node.js) is required to update skills." >&2
  exit 1
fi

if [[ "${1:-}" == "--list" ]]; then
  echo "==> npx skills list"
  exec npx skills list
fi

cat >&2 <<'NOTE'
warning: this moves every installed skill to its latest upstream version — a mutable
operation. It does NOT update config/skills.lock.json, which is the pinned record Aegis
consumes. After updating, re-pin with `bin/subagents-catalog lock` and review the diff.
NOTE

echo "==> npx skills update   (syncing all installed skills to latest)"
npx skills update

echo ""
echo "Registry skills updated."
echo "Reminder: re-run 'bash install.sh' to redistribute local skills (e.g. tailwind),"
echo "and 'bin/subagents-catalog lock' to refresh the pinned provenance record."
