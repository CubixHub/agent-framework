#!/usr/bin/env bash
# Stop the orchestration daemon tmux session.
# Logs reason to /tmp/orchestration-daemon-master.log before killing.

set -euo pipefail

SESSION="orchestration-daemon"
LOG="/tmp/orchestration-daemon-master.log"
REASON="${1:-operator-stop}"

if ! tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "[stop] no session '$SESSION' running"
  exit 0
fi

ts="$(date -Is)"
{
  echo ""
  echo "==== STOP $ts reason=$REASON ===="
} >>"$LOG"

tmux kill-session -t "$SESSION"
echo "[stop] killed session '$SESSION' (reason=$REASON)"
