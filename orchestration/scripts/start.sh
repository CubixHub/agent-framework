#!/usr/bin/env bash
# Launch the orchestration daemon in a long-running tmux session.
#
# Env:
#   PROJECT_DIR  — defaults to PWD; the daemon's working directory.
#   ORCH_WORKFLOW — defaults to $PROJECT_DIR/orchestration/WORKFLOW.md
#   LINEAR_API_KEY (or PLANE_*) — required by the configured pm_provider.
#
# Idempotent: if `orchestration-daemon` tmux session exists, prints and exits.

set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-$PWD}"
ORCH_WORKFLOW="${ORCH_WORKFLOW:-$PROJECT_DIR/orchestration/WORKFLOW.md}"
SESSION="orchestration-daemon"
LOG="/tmp/orchestration-daemon-master.log"

if ! command -v tmux >/dev/null; then
  echo "ERROR: tmux not installed" >&2
  exit 2
fi
if ! [ -f "$ORCH_WORKFLOW" ]; then
  echo "ERROR: workflow not found at $ORCH_WORKFLOW" >&2
  echo "Hint: cp $PROJECT_DIR/orchestration/WORKFLOW.md.tmpl $ORCH_WORKFLOW"
  exit 3
fi

if tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "[start] session '$SESSION' already running; tail $LOG"
  exit 0
fi

# Make `python -m orchestration.runner` resolvable from $PROJECT_DIR.
CMD="cd '$PROJECT_DIR' && PYTHONPATH='$PROJECT_DIR' \
  python -m orchestration.runner --workflow '$ORCH_WORKFLOW' 2>&1 | tee -a '$LOG'"

tmux new-session -d -s "$SESSION" "$CMD"
echo "[start] session '$SESSION' launched; tailing $LOG"
echo "       tmux attach -t $SESSION   # to attach"
