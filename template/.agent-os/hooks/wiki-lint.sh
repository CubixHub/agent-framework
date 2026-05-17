#!/usr/bin/env bash
# wiki-lint.sh — scan for broken [[wikilinks]]. Informational only — never blocks.
set -euo pipefail

input=$(cat)
file=$(echo "$input" | jq -r '.tool_input.file_path // empty' 2>/dev/null || true)
[ -z "$file" ] && exit 0
[[ "$file" != *.md ]] && exit 0
[[ "$file" != *"/wiki/"* ]] && exit 0
[ ! -f "$file" ] && exit 0

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-${DROID_PROJECT_DIR:-${PROJECT_DIR:-$PWD}}}"
WIKI="$PROJECT_DIR/wiki"

broken=()
while IFS= read -r link; do
  base="${link#\[\[}"; base="${base%\]\]}"; base="${base%%|*}"; base="${base%%#*}"
  for path in "$base" "concepts/$base" "entities/$base" "sources/$base" "questions/$base" "plan/$base"; do
    [ -f "$WIKI/${path}.md" ] && continue 2
  done
  broken+=("$link")
done < <(grep -oE '\[\[[^]]+\]\]' "$file" 2>/dev/null || true)

if [ ${#broken[@]} -gt 0 ]; then
  msg="wiki-lint: broken wikilinks in $(basename "$file"): ${broken[*]}"
  printf '{"systemMessage":"%s"}\n' "$msg"
fi
exit 0
