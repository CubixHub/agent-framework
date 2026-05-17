#!/usr/bin/env bash
# pre-commit.sh — local guard: lint + typecheck + format check.
# Forbids --no-verify bypass. Install with: cp .agent-os/hooks/pre-commit.sh .git/hooks/pre-commit
set -euo pipefail

FAIL=0
fail() { echo "[FAIL] $*"; FAIL=1; }

# Best-effort detection of stack; run what's present.
if [ -f package.json ]; then
  if grep -q '"lint"' package.json; then npm run -s lint || fail "lint"; fi
  if grep -q '"typecheck"' package.json; then npm run -s typecheck || fail "typecheck"; fi
fi

if [ -f pyproject.toml ] || [ -f setup.py ]; then
  command -v ruff >/dev/null && (ruff check . || fail "ruff")
  command -v mypy >/dev/null && (mypy --strict . 2>/dev/null || fail "mypy")
fi

if [ -f Cargo.toml ]; then
  command -v cargo >/dev/null && (cargo clippy --quiet -- -D warnings || fail "clippy")
fi

# Format check (no auto-write — that's post-edit.sh's job)
if [ -f package.json ] && command -v prettier >/dev/null; then
  prettier --check . >/dev/null 2>&1 || fail "prettier"
fi

[ $FAIL -eq 0 ] || { echo "Commit blocked. Fix issues and retry. --no-verify is forbidden."; exit 1; }
exit 0
