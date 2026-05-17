"""Minimal pytest invariants for RuntimeState.

Covers:
  - can_claim refuses already-claimed / already-running issues
  - TERMINAL_VERDICTS block re-claim; non-terminal verdicts re-enter
  - mark_completed releases the slot even when called from an exception path
  - capacity cap (max_concurrent) prevents over-claim
"""
from __future__ import annotations

import time

from orchestration.state import (CompletionInfo, RuntimeState, RunSession,
                                 TERMINAL_VERDICTS)
from orchestration.pm_adapters.base import Issue


def _mk_issue(iid: str = "I-1", state: str = "Agent Queue") -> Issue:
    return Issue(id=iid, title="t", body="b", state=state, labels=["@x"])


def test_can_claim_initial_true():
    s = RuntimeState()
    assert s.can_claim(_mk_issue(), max_concurrent=3) is True


def test_can_claim_blocks_when_already_claimed():
    s = RuntimeState()
    i = _mk_issue()
    s.mark_claimed(i)
    assert s.can_claim(i, max_concurrent=3) is False


def test_can_claim_blocks_when_running():
    s = RuntimeState()
    i = _mk_issue()
    s.mark_claimed(i)
    s.mark_running(i, RunSession(
        issue_id=i.id, workspace="/tmp/x", started_at=time.time(),
        agent_role="x", cli_provider="claude", iteration=1,
    ))
    assert s.can_claim(i, max_concurrent=3) is False


def test_terminal_verdict_blocks_reclaim():
    s = RuntimeState()
    i = _mk_issue()
    s.mark_completed(CompletionInfo(
        issue_id=i.id, verdict="PASS", exit_code=0, duration_s=1.0,
    ))
    assert s.can_claim(i, max_concurrent=3) is False
    # all TERMINAL_VERDICTS should block
    for v in TERMINAL_VERDICTS:
        s.completed.clear()
        s.mark_completed(CompletionInfo(issue_id=i.id, verdict=v,
                                        exit_code=0, duration_s=0))
        assert s.can_claim(i, max_concurrent=3) is False, v


def test_non_terminal_verdicts_allow_reentry():
    s = RuntimeState()
    i = _mk_issue()
    for v in ("NEEDS_HUMAN", "CONTINUE"):
        s.completed.clear()
        s.mark_completed(CompletionInfo(issue_id=i.id, verdict=v,
                                        exit_code=0, duration_s=0))
        assert s.can_claim(i, max_concurrent=3) is True, v


def test_slot_release_on_exception_path():
    """Simulate the runner's try/finally: an exception while running must
    still result in mark_completed releasing the slot."""
    s = RuntimeState()
    i = _mk_issue()
    s.mark_claimed(i)
    s.mark_running(i, RunSession(
        issue_id=i.id, workspace="/tmp/x", started_at=time.time(),
        agent_role="x", cli_provider="claude", iteration=1,
    ))
    try:
        raise RuntimeError("boom")
    except RuntimeError:
        s.mark_completed(CompletionInfo(
            issue_id=i.id, verdict="ABORTED_BY_RECONCILIATION",
            exit_code=-1, duration_s=0.0,
        ))
    assert i.id not in s.running
    assert i.id not in s.claimed
    assert s.slots_used() == 0


def test_capacity_cap():
    s = RuntimeState()
    a, b, c, d = (_mk_issue(f"I-{n}") for n in (1, 2, 3, 4))
    for x in (a, b, c):
        s.mark_claimed(x)
    assert s.can_claim(d, max_concurrent=3) is False
