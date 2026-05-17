#!/usr/bin/env bash
# Plane bootstrap — creates the 8 canonical workflow states + canonical
# labels for the orchestration daemon. Idempotent: skips existing items.
#
# Usage:
#   source integrations/plane/.env
#   bash integrations/plane/bootstrap.sh [--dry-run]

set -euo pipefail

DRY_RUN="${1:-}"

: "${PLANE_API_KEY:?PLANE_API_KEY is required}"
: "${PLANE_WORKSPACE_SLUG:?PLANE_WORKSPACE_SLUG is required}"
: "${PLANE_PROJECT_ID:?PLANE_PROJECT_ID is required}"
API_BASE="${PLANE_API_BASE_URL:-https://api.plane.so/api/v1}"
PREFIX="$API_BASE/workspaces/$PLANE_WORKSPACE_SLUG/projects/$PLANE_PROJECT_ID"

_get() {
  curl -fsS -H "X-API-Key: $PLANE_API_KEY" "$1"
}
_post() {
  curl -fsS -X POST -H "X-API-Key: $PLANE_API_KEY" \
    -H "Content-Type: application/json" -d "$2" "$1"
}

# (state_name, group, color)
STATES=(
  "Triage|backlog|#9090a0"
  "Agent Queue|unstarted|#7fa8d8"
  "Processing|started|#d8b87f"
  "Evaluating|started|#d87fb8"
  "Parent AI Review|started|#a87fd8"
  "Human Approval|started|#d8d87f"
  "Completed|completed|#7fd896"
  "Failed|cancelled|#d87f7f"
)

existing="$(_get "$PREFIX/states/" \
  | python3 -c "import sys,json;d=json.load(sys.stdin);r=d.get('results',d);print('|'.join(s['name'] for s in r))")"

for entry in "${STATES[@]}"; do
  IFS='|' read -r name group color <<<"$entry"
  if [[ "|$existing|" == *"|$name|"* ]]; then
    echo "[bootstrap] state '$name' exists; skipping"
    continue
  fi
  payload="{\"name\":\"$name\",\"group\":\"$group\",\"color\":\"$color\"}"
  if [[ "$DRY_RUN" == "--dry-run" ]]; then
    echo "[dry-run] would create state '$name' (group=$group)"
    continue
  fi
  _post "$PREFIX/states/" "$payload" >/dev/null
  echo "[bootstrap] created state '$name' (group=$group)"
done

LABELS=(
  # Agent roles (match agents/<name>/AGENT.md)
  "@architect" "@implementer" "@reviewer" "@tester" "@researcher"
  "@ml-engineer" "@scrutinizer" "@parent-ai" "@wiki-curator"
  "@security-auditor" "@prompt-engineer" "@orchestration-lead"
  "@cron-architect" "@inference-deployer" "@training-orchestrator"
  "@silent-failure-hunter" "@team-debugger" "@test-coverage-analyst"
  # Type / priority / phase / gate
  "type:feature" "type:bug" "type:tech-debt" "type:research" "type:infra" "type:docs"
  "prio:P0" "prio:P1" "prio:P2" "prio:P3"
  "phase:0" "phase:1" "phase:2" "phase:3" "phase:4" "phase:5"
  "gate:proxy-pass" "gate:phase-exit" "gate:human-approval"
)

existing_lbls="$(_get "$PREFIX/labels/" \
  | python3 -c "import sys,json;d=json.load(sys.stdin);r=d.get('results',d);print('|'.join(l['name'] for l in r))")"

for lbl in "${LABELS[@]}"; do
  if [[ "|$existing_lbls|" == *"|$lbl|"* ]]; then
    echo "[bootstrap] label '$lbl' exists; skipping"
    continue
  fi
  if [[ "$DRY_RUN" == "--dry-run" ]]; then
    echo "[dry-run] would create label '$lbl'"
    continue
  fi
  _post "$PREFIX/labels/" "{\"name\":\"$lbl\",\"color\":\"#909090\"}" >/dev/null
  echo "[bootstrap] created label '$lbl'"
done

rm -f /tmp/plane_state.json
echo "[bootstrap] done. Cache reset; next daemon tick will re-fetch."
