"""Abstract base for PM-tool adapters (Linear / Plane).

A PMAdapter exposes four operations to the runner:

  fetch_queue()                  -> list[Issue]
      Returns issues currently in any state listed under
      `eligible_states` in WORKFLOW.md, with at least one
      `@<role>` label that maps to a known subagent.

  claim(issue, comment)          -> bool
      Atomic mutation: transition `issue` from its current state
      into the canonical "Processing" state and post `comment`.
      Returns True if claim succeeded, False on race/conflict.

  transition_state(issue, state, comment) -> bool
      Move `issue` to `state`, posting `comment` (the verdict comment
      block) atomically when possible.

  post_comment(issue, body)      -> bool
      Append a comment without transitioning state.

The Issue dataclass is the canonical, PM-agnostic shape. Each adapter
is responsible for translating native fields onto it.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Issue:
    id: str                  # human-readable, e.g. "LLM-244" or Plane sequence id
    title: str
    body: str
    state: str               # canonical name, e.g. "Agent Queue"
    labels: list[str] = field(default_factory=list)
    pm_native: dict[str, Any] = field(default_factory=dict)


class PMAdapter(ABC):
    name: str = "base"

    @abstractmethod
    def fetch_queue(self) -> list[Issue]:
        ...

    @abstractmethod
    def claim(self, issue: Issue, comment: str = "") -> bool:
        ...

    @abstractmethod
    def transition_state(self, issue: Issue, state: str, comment: str = "") -> bool:
        ...

    @abstractmethod
    def post_comment(self, issue: Issue, body: str) -> bool:
        ...
