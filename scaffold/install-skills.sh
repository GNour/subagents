#!/usr/bin/env bash
# Install every skills.sh skill referenced by the fleet (the `owner/repo` ids in
# each agent's frontmatter). Single-word slugs are bundled/local and skipped.
#
#   bash scaffold/install-skills.sh            # install all referenced skills
#   bash scaffold/install-skills.sh --dry-run  # just list them
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENTS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)/agents"

DRY_RUN=0
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=1

# Collect all `owner/repo` skill ids from agent frontmatter, dedup, sort.
mapfile -t SKILLS < <(grep -rhoE '^\s*-\s+[a-z0-9._-]+/[a-z0-9._-]+\s*$' "$AGENTS_DIR" \
  | sed -E 's/^\s*-\s+//; s/\s+$//' | sort -u)

echo "Found ${#SKILLS[@]} installable skills referenced by the fleet."

if [[ $DRY_RUN -eq 1 ]]; then
  printf '  %s\n' "${SKILLS[@]}"
  echo "(dry run — nothing installed)"
  exit 0
fi

if ! command -v npx >/dev/null 2>&1; then
  echo "error: npx (Node.js) is required to install skills." >&2
  echo "Install Node.js, or install skills manually with: npx skills add <owner/repo>" >&2
  exit 1
fi

cat >&2 <<'NOTE'
warning: `npx skills add` resolves each skill at its current upstream HEAD, not a
pinned revision. The pinned supply-chain record lives in config/skills.lock.json
(regenerate with `bin/subagents-catalog lock`). This convenience installer is
separate from that catalog and is optional.
NOTE

failures=()
for s in "${SKILLS[@]}"; do
  echo "==> npx skills add $s"
  if ! npx skills add "$s"; then
    failures+=("$s")
  fi
done

if (( ${#failures[@]} > 0 )); then
  echo "error: ${#failures[@]} skill install(s) failed; catalog install is incomplete:" >&2
  printf '  ! %s\n' "${failures[@]}" >&2
  exit 1
fi

echo "Done. Skills installed globally; run your harness to verify."
