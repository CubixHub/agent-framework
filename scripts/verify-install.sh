#!/usr/bin/env bash
# verify-install.sh — check that all CLIs and helpers are present
set -euo pipefail

C_GREEN='\033[0;32m'; C_RED='\033[0;31m'; C_YELLOW='\033[1;33m'; C_OFF='\033[0m'
ok()    { printf "${C_GREEN}OK${C_OFF}   %-12s  %s\n" "$1" "$2"; }
miss()  { printf "${C_RED}MISS${C_OFF} %-12s  %s\n" "$1" "$2"; }
warn()  { printf "${C_YELLOW}WARN${C_OFF} %-12s  %s\n" "$1" "$2"; }

echo "== CLI binaries =="
for bin in claude codex pi; do
  if command -v "$bin" >/dev/null 2>&1; then
    ok "$bin" "$(command -v "$bin")"
  else
    miss "$bin" "not on PATH"
  fi
done

echo
echo "== Helpers =="
for bin in jq tmux git python3; do
  if command -v "$bin" >/dev/null 2>&1; then
    ok "$bin" "$(command -v "$bin")"
  else
    miss "$bin" "required for hooks/orchestration"
  fi
done

echo
echo "== Project layout =="
for p in .agent-os AGENTS.md wiki; do
  if [ -e "$p" ]; then ok "$p" "present"; else miss "$p" "missing — run init-project.sh"; fi
done

echo
echo "== PM env =="
if [ -f .env ]; then
  if grep -q "_API_KEY=" .env 2>/dev/null; then ok ".env" "API key present"; else warn ".env" "no API key set"; fi
else
  warn ".env" "no .env file (PM features will be disabled)"
fi
