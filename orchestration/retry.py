"""Exponential backoff for failed claim/spawn/verdict cycles.

The daemon increments `retry_attempts[issue_id]` on each FAIL verdict.
When attempts >= max_retries, the runner posts a final FAIL verdict
(verdict comment notes the exhaustion) and routes the issue to the
Failed state. Otherwise it schedules `retry_after[issue_id]` and skips
the issue until the window passes.
"""
from __future__ import annotations

import time

BASE_SECONDS = 60       # first retry waits 60s
CAP_SECONDS = 3600      # cap at 1 hour
MAX_RETRIES = 3


def compute_retry_after(attempt: int,
                        base: int = BASE_SECONDS,
                        cap: int = CAP_SECONDS) -> float:
    """Return the absolute epoch timestamp to retry at.

    attempt: 1-indexed retry counter (1 = first retry).
    Backoff: base * 2**(attempt-1), capped at `cap`.
    """
    if attempt < 1:
        attempt = 1
    delay = min(base * (2 ** (attempt - 1)), cap)
    return time.time() + delay


def is_exhausted(attempt: int, max_retries: int = MAX_RETRIES) -> bool:
    """True once the FAIL verdict should route to the terminal Failed state."""
    return attempt >= max_retries
