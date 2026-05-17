"""RuntimeState — in-memory daemon bookkeeping.

Tracks claimed/running/completed issues, retry budget, backoff windows.
The `can_claim()` rule is the heart of the contract: only TERMINAL_VERDICTS
short-circuit re-claim, so NEEDS_HUMAN / bare CONTINUE re-enter the pool.

Slot release is guaranteed by the runner's try/finally; mark_completed()
must be called even on exception paths so the slot becomes free.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Optional


TERMINAL_VERDICTS = {
    "PASS",
    "PROXY_PASS",
    "HUMAN_APPROVAL_REQUIRED",
    "FAIL",
    "CONTINUE_EXHAUSTED",
    "ABORTED_BY_RECONCILIATION",
    "OPERATOR_ABORTED",
}

# Non-terminal verdicts — re-enter the pool on next tick.
REENTRY_VERDICTS = {"NEEDS_HUMAN", "CONTINUE"}


@dataclass
class Issue:
    """PM-tool-agnostic issue record."""
    id: str
    title: str
    body: str
    state: str
    labels: list[str] = field(default_factory=list)
    pm_native: dict[str, Any] = field(default_factory=dict)   # raw PM payload


@dataclass
class RunSession:
    """A subprocess currently spawned for an issue."""
    issue_id: str
    workspace: str
    started_at: float
    agent_role: str
    cli_provider: str
    iteration: int


@dataclass
class CompletionInfo:
    """Outcome of one full claim->verdict iteration."""
    issue_id: str
    verdict: str
    exit_code: int
    duration_s: float
    journal_path: Optional[str] = None
    completed_at: float = field(default_factory=time.time)

    @property
    def is_terminal(self) -> bool:
        return self.verdict in TERMINAL_VERDICTS


@dataclass
class RuntimeState:
    """All in-memory bookkeeping for the daemon."""
    claimed: dict[str, Issue] = field(default_factory=dict)
    running: dict[str, RunSession] = field(default_factory=dict)
    completed: dict[str, CompletionInfo] = field(default_factory=dict)
    retry_attempts: dict[str, int] = field(default_factory=dict)
    retry_after: dict[str, float] = field(default_factory=dict)

    # ---------- capacity / eligibility ----------

    def slots_used(self) -> int:
        return len(self.claimed) + len(self.running)

    def can_claim(self, issue: Issue, max_concurrent: int) -> bool:
        iid = issue.id
        if iid in self.claimed or iid in self.running:
            return False
        if iid in self.completed and self.completed[iid].is_terminal:
            return False
        if iid in self.retry_after and time.time() < self.retry_after[iid]:
            return False
        if self.slots_used() >= max_concurrent:
            return False
        return True

    # ---------- lifecycle transitions ----------

    def mark_claimed(self, issue: Issue) -> None:
        self.claimed[issue.id] = issue
        # If we're re-claiming a non-terminal completion, scrub it so the
        # slot becomes available next time.
        self.completed.pop(issue.id, None)

    def mark_running(self, issue: Issue, session: RunSession) -> None:
        self.running[issue.id] = session
        self.claimed.pop(issue.id, None)

    def mark_completed(self, info: CompletionInfo) -> None:
        """Always called from a finally block. Releases the slot."""
        self.completed[info.issue_id] = info
        self.running.pop(info.issue_id, None)
        self.claimed.pop(info.issue_id, None)

    def increment_retry(self, issue_id: str) -> int:
        n = self.retry_attempts.get(issue_id, 0) + 1
        self.retry_attempts[issue_id] = n
        return n

    def schedule_retry(self, issue_id: str, retry_after_ts: float) -> None:
        self.retry_after[issue_id] = retry_after_ts

    def reset_retry(self, issue_id: str) -> None:
        self.retry_attempts.pop(issue_id, None)
        self.retry_after.pop(issue_id, None)
