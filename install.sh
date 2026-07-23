#!/usr/bin/env bash
# Install the subagent fleet into AI coding harnesses.
#
#   bash install.sh                     # all detected harnesses, global
#   bash install.sh --claude --opencode # only these
#   bash install.sh --codex             # Codex only (converts to TOML)
#   bash install.sh --pi                # pi only (prompt templates)
#   bash install.sh --all --project     # into this repo instead of $HOME
#   bash install.sh --all --dry-run     # preview, write nothing
#
# Targets:
#   Claude Code  ~/.claude/agents/<dept>/<name>.md   (native, verbatim)
#   opencode     ~/.config/opencode/agent/<name>.md
#   Codex        ~/.codex/agents/<name>.toml          (best-effort conversion)
#   pi           ~/.pi/agent/prompts/<name>.md
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v python3 >/dev/null 2>&1; then
  echo "error: python3 is required to run the installer." >&2
  exit 1
fi

exec python3 "$SCRIPT_DIR/scaffold/_install.py" "$@"
