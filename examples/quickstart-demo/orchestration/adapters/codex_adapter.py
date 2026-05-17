"""Codex (OpenAI) CLI adapter.

Invocation:
  codex -p "<prompt>"

The Codex CLI reads AGENTS.md + CODEX.md from the working directory.
Same envelope as the Claude adapter: last-line VERDICT parse, stall
detection, exit code. Multi-turn is managed by the runner re-spawning
(Codex has its own continuation flag — pass it through `extra_args`
when wiring this adapter in `runner._build_cli_adapter`).
"""
from __future__ import annotations

from .base import CLIAdapter, SubprocessResult


class CodexAdapter(CLIAdapter):
    name = "codex"

    def __init__(self,
                 bin_path: str = "codex",
                 stall_timeout_ms: int = 1_800_000,
                 extra_args: list[str] | None = None) -> None:
        self.bin_path = bin_path
        self.stall_timeout_ms = stall_timeout_ms
        self.extra_args = extra_args or []

    def spawn(self,
              prompt: str,
              workspace: str,
              max_turns: int) -> SubprocessResult:
        argv = [self.bin_path]
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
        )
