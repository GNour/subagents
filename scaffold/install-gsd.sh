#!/usr/bin/env bash
# Install the GSD (Get Shit Done) spec-driven workflow framework.
#
# GSD is the fleet's orchestration layer (plan -> execute -> verify), used by
# company-orchestrator, tech-lead, and product-owner. It is NOT a skills.sh package;
# it ships its own installer and deploys into the harness's skills dir (.claude/skills, etc).
#
# Two distributions:
#   - Original (Claude Code):        npx get-shit-done-cc@latest
#   - Multi-harness fork (default):  shoootyou/get-shit-done-multi
#     Installs a unified spec-driven system across Claude Code, Codex, and Copilot.
#
#   bash scaffold/install-gsd.sh          # original GSD installer (Claude Code)
#   bash scaffold/install-gsd.sh --multi  # show the multi-harness fork instructions
set -euo pipefail

if ! command -v npx >/dev/null 2>&1; then
  echo "error: npx (Node.js) is required to install GSD." >&2
  exit 1
fi

if [[ "${1:-}" == "--multi" ]]; then
  echo "GSD Multi (multi-harness fork): deploys a unified spec-driven system to"
  echo "Claude Code, Codex, and Copilot with one installer."
  echo ""
  echo "  Repo:    https://github.com/shoootyou/get-shit-done-multi"
  echo "  Install: follow the repo README (template-based installer) for the exact"
  echo "           command for your setup — it changes as the fork evolves."
  exit 0
fi

echo "==> Installing GSD (Get Shit Done) for Claude Code:"
echo "    npx get-shit-done-cc@latest"
echo "    After install, run /gsd-help to start. Flow: /gsd-plan -> /gsd-execute -> /gsd-verify."
echo "    For Codex/opencode/Copilot too, see the multi-harness fork: --multi"
echo ""
exec npx get-shit-done-cc@latest
