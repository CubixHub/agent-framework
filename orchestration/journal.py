"""Per-iteration run journal writer.

Each invocation writes wiki/runs/<issue-id>-iter<n>.md with required
frontmatter (type, agent, verdict, started, duration, exit_code).

The wiki root is $PROJECT_DIR/wiki by default; override with
$ORCH_WIKI_DIR. If the dir doesn't exist it falls back to
/tmp/orchestration-journals/ so the daemon never crashes on a misconfig.
"""
from __future__ import annotations

import os
import datetime as _dt
from pathlib import Path


def _wiki_root() -> Path:
    env = os.environ.get("ORCH_WIKI_DIR")
    if env:
        return Path(env)
    project = os.environ.get("PROJECT_DIR") or os.getcwd()
    wiki = Path(project) / "wiki"
    if wiki.exists():
        return wiki
    fallback = Path("/tmp/orchestration-journals")
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback


def write_journal(
    issue_id: str,
    iteration: int,
    agent_role: str,
    verdict: str,
    started_iso: str,
    duration_s: float,
    exit_code: int,
    stdout_tail: str,
    stderr_tail: str = "",
    extra: dict | None = None,
) -> str:
    """Write the per-iteration journal file. Returns absolute path."""
    runs = _wiki_root() / "runs"
    runs.mkdir(parents=True, exist_ok=True)
    safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in issue_id)
    path = runs / f"{safe}-iter{iteration}.md"

    extra = extra or {}
    extra_lines = "".join(f"{k}: {v}\n" for k, v in extra.items())
    today = _dt.date.today().isoformat()

    body = (
        "---\n"
        f"type: run\n"
        f"issue: {issue_id}\n"
        f"iteration: {iteration}\n"
        f"agent: {agent_role}\n"
        f"verdict: {verdict}\n"
        f"started: {started_iso}\n"
        f"duration_s: {duration_s:.2f}\n"
        f"exit_code: {exit_code}\n"
        f"updated: {today}\n"
        f"{extra_lines}"
        "---\n\n"
        f"# Run journal — {issue_id} iter {iteration}\n\n"
        f"**Agent:** {agent_role}  \n"
        f"**Verdict:** `{verdict}`  \n"
        f"**Duration:** {duration_s:.2f}s  \n"
        f"**Exit code:** {exit_code}\n\n"
        "## stdout (tail)\n\n"
        "```\n"
        f"{stdout_tail}\n"
        "```\n\n"
    )
    if stderr_tail:
        body += "## stderr (tail)\n\n```\n" + stderr_tail + "\n```\n"
    path.write_text(body, encoding="utf-8")
    return str(path)
