#!/usr/bin/env bash
# Linear bootstrap — creates the 8 canonical workflow states + canonical
# labels for the orchestration daemon. Idempotent: skips existing items.
#
# Usage:
#   source integrations/linear/.env
#   bash integrations/linear/bootstrap.sh [--dry-run]

set -euo pipefail

DRY_RUN="${1:-}"

: "${LINEAR_API_KEY:?LINEAR_API_KEY is required}"
: "${LINEAR_TEAM_KEY:?LINEAR_TEAM_KEY is required}"

API="https://api.linear.app/graphql"

_gql() {
  local payload="$1"
  curl -fsS -X POST "$API" \
    -H "Authorization: $LINEAR_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$payload"
}

team_id="$(_gql "$(cat <<JSON
{"query":"query(\$k:String!){teams(filter:{key:{eq:\$k}}){nodes{id}}}",
 "variables":{"k":"$LINEAR_TEAM_KEY"}}
JSON
)" | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['data']['teams']['nodes'][0]['id'])")"

echo "[bootstrap] team_id=$team_id"

declare -A STATES=(
  ["Triage"]="triage"
  ["Agent Queue"]="unstarted"
  ["Processing"]="started"
  ["Evaluating"]="started"
  ["Parent AI Review"]="started"
  ["Human Approval"]="started"
  ["Completed"]="completed"
  ["Failed"]="canceled"
)

existing="$(_gql "$(cat <<JSON
{"query":"query(\$t:String!){workflowStates(filter:{team:{id:{eq:\$t}}}){nodes{name}}}",
 "variables":{"t":"$team_id"}}
JSON
)" | python3 -c "import sys,json;d=json.load(sys.stdin);print('|'.join(n['name'] for n in d['data']['workflowStates']['nodes']))")"

for name in "${!STATES[@]}"; do
  if [[ "|$existing|" == *"|$name|"* ]]; then
    echo "[bootstrap] state '$name' exists; skipping"
    continue
  fi
  type="${STATES[$name]}"
  if [[ "$DRY_RUN" == "--dry-run" ]]; then
    echo "[dry-run] would create state '$name' (type=$type)"
    continue
  fi
  _gql "$(cat <<JSON
{"query":"mutation(\$t:String!,\$n:String!,\$y:String!){workflowStateCreate(input:{teamId:\$t,name:\$n,type:\$y,color:\"#9090a0\"}){success}}",
 "variables":{"t":"$team_id","n":"$name","y":"$type"}}
JSON
)" >/dev/null
  echo "[bootstrap] created state '$name' (type=$type)"
done

# canonical labels — Framework agent roles + standard taxonomy
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

existing_lbls="$(_gql "$(cat <<JSON
{"query":"query(\$t:String!){issueLabels(filter:{team:{id:{eq:\$t}}}){nodes{name}}}",
 "variables":{"t":"$team_id"}}
JSON
)" | python3 -c "import sys,json;d=json.load(sys.stdin);print('|'.join(n['name'] for n in d['data']['issueLabels']['nodes']))")"

for lbl in "${LABELS[@]}"; do
  if [[ "|$existing_lbls|" == *"|$lbl|"* ]]; then
    echo "[bootstrap] label '$lbl' exists; skipping"
    continue
  fi
  if [[ "$DRY_RUN" == "--dry-run" ]]; then
    echo "[dry-run] would create label '$lbl'"
    continue
  fi
  _gql "$(cat <<JSON
{"query":"mutation(\$t:String!,\$n:String!){issueLabelCreate(input:{teamId:\$t,name:\$n,color:\"#909090\"}){success}}",
 "variables":{"t":"$team_id","n":"$lbl"}}
JSON
)" >/dev/null
  echo "[bootstrap] created label '$lbl'"
done

# refresh the daemon's schema cache
rm -f /tmp/linear_state.json
echo "[bootstrap] done. Cache reset; next daemon tick will re-fetch."
