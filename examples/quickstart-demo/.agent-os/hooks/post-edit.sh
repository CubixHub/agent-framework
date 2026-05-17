#!/usr/bin/env bash
# post-edit.sh — dispatcher fired on Create/Edit/ApplyPatch
# Reads JSON {"tool_input":{"file_path":"..."}} from stdin.
set -euo pipefail

input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty' 2>/dev/null || true)
[ -z "$file_path" ] && exit 0

dir="$(dirname "$0")"

case "$file_path" in
  */wiki/*.md|*/wiki/*/*.md)
    bash "$dir/wiki-lint.sh" <<<"$input"
    ;;
  *.ts|*.tsx|*.js|*.jsx|*.py|*.rs|*.go|*.json|*.yaml|*.yml|*.md)
    bash "$dir/format-on-edit.sh" <<<"$input"
    ;;
esac
exit 0
