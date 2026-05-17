#!/usr/bin/env bash
# format-on-edit.sh — run the language-appropriate formatter and write back.
set -euo pipefail

input=$(cat)
file=$(echo "$input" | jq -r '.tool_input.file_path // empty' 2>/dev/null || true)
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

case "$file" in
  *.ts|*.tsx|*.js|*.jsx|*.json|*.md|*.yaml|*.yml)
    command -v prettier >/dev/null && prettier --write "$file" >/dev/null 2>&1 || true
    ;;
  *.py)
    command -v ruff >/dev/null && ruff format "$file" >/dev/null 2>&1 || \
      (command -v black >/dev/null && black -q "$file" 2>/dev/null) || true
    ;;
  *.rs)
    command -v rustfmt >/dev/null && rustfmt "$file" >/dev/null 2>&1 || true
    ;;
  *.go)
    command -v gofmt >/dev/null && gofmt -w "$file" >/dev/null 2>&1 || true
    ;;
esac
exit 0
