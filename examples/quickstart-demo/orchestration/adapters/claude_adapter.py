"""Claude Code CLI adapter.

Invocation:
  claude --permission-mode bypassPermissions -p "<prompt>"

The Claude CLI reads AGENTS.md + CLAUDE.md from the working directory.
Multi-turn continuation: re-invoke with --continue (Claude tracks
session state via its own session-store; not via our process tree).

This adapter is intentionally single-turn-per-spawn. The runner manages
the turn loop by re-spawning with --continue when verdict == "CONTINUE"
and turns_used < max_turns_per_session.
"""
from __future__ import annotations

import os

from .base import CLIAdapter, SubprocessResult


class ClaudeAdapter(CLIAdapter):
    name = "claude"

    def __init__(self,
                 bin_path: str = "claude",
                 stall_timeout_ms: int = 1_800_000,
                 extra_args: list[str] | None = None) -> None:
        self.bin_path = bin_path
        self.stall_timeout_ms = stall_timeout_ms
        self.extra_args = extra_args or []

    def spawn(self,
              prompt: str,
              workspace: str,
              max_turns: int,
              *,
              continuation: bool = False) -> SubprocessResult:
        argv = [self.bin_path, "--permission-mode", "bypassPermissions"]
        if continuation:
            argv.append("--continue")
        argv.extend(self.extra_args)
        argv.extend(["-p", prompt])
        env = {
            "ORCH_WORKSPACE": workspace,
            "ORCH_MAX_TURNS": str(max_turns),
        }
        stdout, stderr, exit_code, stalled, duration = self.run_with_stall_detection(
            argv,
            cwd=workspace,
            stall_timeout_ms=self.stall_timeout_ms,
            env_overrides=env,
        )
        verdict = self.parse_verdict(stdout) if not stalled else "ABORTED_BY_RECONCILIATION"
        return SubprocessResult(
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            verdict=verdict,
            duration_s=duration,
            stalled=stalled,
            turns_used=1,
            extra={"continuation": continuation},
        )
