"""Orchestration daemon — main loop.

  python -m orchestration.runner --workflow $PROJECT_DIR/orchestration/WORKFLOW.md

30s tick: fetch_queue → for each issue (can_claim → claim → spawn →
parse verdict → route → mark_completed). Try/finally guarantees slot
release. Log to /tmp/orchestration-daemon-master.log.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import logging
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

import yaml  # noqa: F401  # PyYAML is the only non-stdlib dep besides requests

# ---- imports relative to package ----
from .adapters.base import CLIAdapter, SubprocessResult
from .adapters.claude_adapter import ClaudeAdapter
from .adapters.codex_adapter import CodexAdapter
from .adapters.pi_adapter import PiAdapter
from .pm_adapters.base import Issue, PMAdapter
from .pm_adapters.linear_adapter import LinearAdapter
from .pm_adapters.plane_adapter import PlaneAdapter
from . import journal, retry, workspace
from .state import (CompletionInfo, RuntimeState, RunSession,
                    TERMINAL_VERDICTS)

LOG_PATH = os.environ.get("ORCH_LOG_PATH", "/tmp/orchestration-daemon-master.log")


def _setup_logging() -> logging.Logger:
    logger = logging.getLogger("orch")
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    fh = logging.FileHandler(LOG_PATH)
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(sh)
    return logger


LOG = _setup_logging()


# ---- WORKFLOW.md loader ----

YAML_FENCE = re.compile(r"```yaml\s*\n(.*?)```", re.DOTALL)


def load_workflow(path: str) -> dict[str, Any]:
    text = Path(path).read_text(encoding="utf-8")
    m = YAML_FENCE.search(text)
    raw = m.group(1) if m else text
    return yaml.safe_load(raw) or {}


# ---- adapter factories ----

def build_pm_adapter(cfg: dict) -> PMAdapter:
    provider = cfg.get("pm_provider", "linear")
    eligible = cfg.get("eligible_states", ["Agent Queue"])
    if provider == "linear":
        return LinearAdapter(eligible_states=eligible)
    if provider == "plane":
        return PlaneAdapter(eligible_states=eligible)
    raise ValueError(f"unknown pm_provider: {provider}")


def build_cli_adapter(role: str, cfg: dict) -> CLIAdapter:
    providers = cfg.get("cli_provider", {})
    provider = providers.get(role) or providers.get("default", "claude")
    bins = cfg.get("cli_bin", {})
    stall = int(cfg.get("stall_timeout_ms", 1_800_000))
    if provider == "claude":
        return ClaudeAdapter(bin_path=bins.get("claude", "claude"), stall_timeout_ms=stall)
    if provider == "codex":
        return CodexAdapter(bin_path=bins.get("codex", "codex"), stall_timeout_ms=stall)
    if provider == "pi":
        return PiAdapter(bin_path=bins.get("pi", "pi"), stall_timeout_ms=stall)
    raise ValueError(f"unknown cli_provider for role={role}: {provider}")


# ---- H3 + role resolution ----

ROLE_LABEL_RX = re.compile(r"^@([\w\-]+)$")


def resolve_role(issue: Issue, cfg: dict) -> str | None:
    """Apply H3 routing first, then label-based routing."""
    routing = cfg.get("agent_role_routing", {})
    # H3: state-forced agent overrides label.
    if issue.state == "Parent AI Review" and "parent-ai" in routing:
        return "parent-ai"
    if issue.state == "Evaluating" and "@scrutinizer" in issue.labels and "scrutinizer" in routing:
        return "scrutinizer"
    for lbl in issue.labels:
        m = ROLE_LABEL_RX.match(lbl)
        if m and m.group(1) in routing:
            return m.group(1)
    return None


# ---- acceptance criteria parser ----

AC_RX = re.compile(r"(?:Acceptance|Acceptance criteria)\s*:?\s*\n(.*?)(?:\n\s*\n|\Z)",
                   re.IGNORECASE | re.DOTALL)


def parse_acceptance(body: str) -> str:
    m = AC_RX.search(body or "")
    return (m.group(1).strip() if m else "(not found in issue body)")


# ---- prompt renderer ----

def render_prompt(template: str, issue: Issue, *, agent_role: str,
                  workspace_path: str, iteration: int) -> str:
    return template.format(
        issue_id=issue.id,
        issue_title=issue.title,
        issue_body=issue.body or "(empty)",
        agent_role=agent_role,
        workspace_path=workspace_path,
        iteration=iteration,
        acceptance_criteria=parse_acceptance(issue.body),
    )


# ---- verdict comment + state routing ----

def format_verdict_comment(verdict: str, artifacts: str, summary: str, gate: str) -> str:
    return (
        f"VERDICT: {verdict}\n"
        f"Artifacts: {artifacts}\n"
        f"Summary: {summary}\n"
        f"Gate ref: {gate}\n"
    )


def route_verdict(state: RuntimeState, issue: Issue, result: SubprocessResult,
                  cfg: dict, pm: PMAdapter, journal_path: str) -> None:
    """Apply the verdict-routing table, with retry handling for FAIL."""
    verdict = result.verdict
    routing = cfg.get("verdict_routing", {})
    max_retries = int(cfg.get("max_retries", retry.MAX_RETRIES))
    base = int(cfg.get("retry_base_seconds", retry.BASE_SECONDS))

    if verdict == "FAIL":
        attempt = state.increment_retry(issue.id)
        if retry.is_exhausted(attempt, max_retries):
            target = routing.get("FAIL", "Failed")
            comment = format_verdict_comment(
                "FAIL", journal_path,
                f"Retry budget exhausted ({attempt}/{max_retries}).",
                "retry-budget")
            pm.transition_state(issue, target, comment)
        else:
            ts = retry.compute_retry_after(attempt, base=base)
            state.schedule_retry(issue.id, ts)
            pm.post_comment(issue,
                            f"FAIL attempt {attempt}/{max_retries}; retry after "
                            f"{_dt.datetime.fromtimestamp(ts).isoformat()}")
        return

    if verdict == "CONTINUE":
        # stay in Processing; will re-enter on next tick
        return

    # All other verdicts: simple routing.
    target = routing.get(verdict)
    if not target:
        LOG.warning("no routing entry for verdict=%s (issue=%s)", verdict, issue.id)
        return
    comment = format_verdict_comment(verdict, journal_path,
                                     f"Daemon-routed via verdict {verdict}.",
                                     "see-issue-body")
    pm.transition_state(issue, target, comment)
    if verdict in ("PASS", "PROXY_PASS"):
        state.reset_retry(issue.id)


# ---- per-issue processing (try/finally guarantees slot release) ----

def process_issue(issue: Issue, state: RuntimeState, cfg: dict, pm: PMAdapter) -> None:
    role = resolve_role(issue, cfg)
    if not role:
        LOG.info("skip %s — no @<role> label and no H3 force", issue.id)
        return
    if not state.can_claim(issue, int(cfg.get("max_concurrent_agents", 3))):
        return

    # 1. claim
    if not pm.claim(issue, comment=f"Daemon claimed via role={role}"):
        LOG.warning("claim mutation failed for %s", issue.id)
        return
    state.mark_claimed(issue)

    iteration = state.retry_attempts.get(issue.id, 0) + 1
    ws_path = workspace.ensure_workspace(issue.id)
    started = time.time()
    session = RunSession(issue_id=issue.id, workspace=ws_path,
                         started_at=started, agent_role=role,
                         cli_provider="(pending)", iteration=iteration)
    state.mark_running(issue, session)

    verdict = "ABORTED_BY_RECONCILIATION"
    duration = 0.0
    exit_code = -1
    jpath: str | None = None

    try:
        cli = build_cli_adapter(role, cfg)
        session.cli_provider = cli.name
        prompt = render_prompt(
            cfg.get("prompt_template", ""), issue,
            agent_role=role, workspace_path=ws_path, iteration=iteration,
        )
        max_turns = int(cfg.get("max_turns_per_session", 10))
        result = cli.spawn(prompt, ws_path, max_turns)
        verdict = result.verdict
        duration = result.duration_s
        exit_code = result.exit_code
        jpath = journal.write_journal(
            issue_id=issue.id, iteration=iteration, agent_role=role,
            verdict=verdict,
            started_iso=_dt.datetime.fromtimestamp(started).isoformat(),
            duration_s=duration, exit_code=exit_code,
            stdout_tail=result.stdout[-4000:],
            stderr_tail=result.stderr[-2000:],
            extra={"cli_provider": cli.name, "stalled": result.stalled},
        )
        route_verdict(state, issue, result, cfg, pm, jpath)
    except Exception as exc:
        LOG.exception("process_issue %s raised: %s", issue.id, exc)
        try:
            pm.post_comment(issue, f"Daemon error: {exc!r} (slot released).")
        except Exception:
            pass
    finally:
        info = CompletionInfo(
            issue_id=issue.id, verdict=verdict, exit_code=exit_code,
            duration_s=duration, journal_path=jpath,
        )
        state.mark_completed(info)
        LOG.info("done %s verdict=%s duration=%.1fs", issue.id, verdict, duration)


# ---- main loop ----

def tick(state: RuntimeState, cfg: dict, pm: PMAdapter) -> None:
    queue = pm.fetch_queue()
    LOG.info("tick: queue=%d claimed=%d running=%d completed=%d",
             len(queue), len(state.claimed), len(state.running), len(state.completed))
    for issue in queue:
        try:
            process_issue(issue, state, cfg, pm)
        except Exception as exc:
            LOG.exception("tick: failure on %s: %s", issue.id, exc)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--workflow", required=True, help="Path to WORKFLOW.md")
    p.add_argument("--once", action="store_true", help="Run a single tick and exit")
    args = p.parse_args(argv)
    state = RuntimeState()
    LOG.info("orchestration daemon starting; workflow=%s", args.workflow)
    while True:
        cfg = load_workflow(args.workflow)   # hot reload every tick
        pm = build_pm_adapter(cfg)
        try:
            tick(state, cfg, pm)
        except Exception as exc:
            LOG.exception("tick crashed: %s", exc)
        if args.once:
            return 0
        time.sleep(int(cfg.get("poll_interval_seconds", 30)))


if __name__ == "__main__":
    sys.exit(main())
