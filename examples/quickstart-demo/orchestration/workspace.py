"""Per-issue workspace at /tmp/orchestration-workspaces/<id>/.

Each spawn gets a clean cwd so concurrent runs don't trample each other.
The workspace is NOT deleted on completion by default — operator may
want to inspect artifacts. Call `cleanup(issue_id)` explicitly if you
want to reclaim disk.
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path

ROOT = Path(os.environ.get("ORCH_WORKSPACE_ROOT", "/tmp/orchestration-workspaces"))


def ensure_workspace(issue_id: str) -> str:
    """Create (or reuse) the workspace directory for `issue_id`. Returns abs path."""
    safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in issue_id)
    path = ROOT / safe
    path.mkdir(parents=True, exist_ok=True)
    return str(path)


def cleanup(issue_id: str) -> None:
    """Best-effort removal of an issue's workspace."""
    safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in issue_id)
    path = ROOT / safe
    if path.exists():
        shutil.rmtree(path, ignore_errors=True)
