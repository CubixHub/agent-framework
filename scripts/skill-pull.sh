#!/usr/bin/env bash
# skill-pull.sh — fetch/refresh a named skill from Framework into a project
# Usage: bash scripts/skill-pull.sh <skill-name> [target-project-dir]
set -euo pipefail

SKILL="${1:?usage: skill-pull.sh <skill-name> [target]}"
TARGET="${2:-$PWD}"
FRAMEWORK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$FRAMEWORK_DIR/skills/$SKILL"
DST="$TARGET/.agent-os/skills/$SKILL"

[ -d "$SRC" ] || { echo "Unknown skill: $SKILL (see $FRAMEWORK_DIR/skills/)"; exit 1; }
mkdir -p "$(dirname "$DST")"
rm -rf "$DST"
cp -r "$SRC" "$DST"
echo "OK pulled $SKILL → $DST"
