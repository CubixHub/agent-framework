"""Pi (pi.dev) CLI adapter — two modes.

Install:
  npm install -g @earendil-works/pi-coding-agent
  # OR
  curl -fsSL https://pi.dev/install.sh | sh

Modes:
  (a) Simple:  `pi -p "<prompt>"`  — same envelope as Claude/Codex
  (b) JSON:    `pi --mode json`   — newline-delimited JSON over stdin/stdout
                                    PREFERRED for orchestration

JSON envelope (per line):
  {"type": "thinking" | "tool_use" | "turn_complete" | "final",
   "verdict": "PASS"|...,        # present on type=final
   "content": "..."}             # free-form

Pi sub-agents / MCP / plan-mode require pre-install of Pi extensions:
  pi extension install @earendil-works/sub-agents
  pi extension install @earendil-works/plan-mode
  pi extension install @earendil-works/mcp-bridge
(See https://pi.dev/extensions for the full catalog.)

Pi reads AGENTS.md + SYSTEM.md from the cwd.
"""
from __future__ import annotations

import json

from .base import CLIAdapter, SubprocessResult


class PiAdapter(CLIAdapter):
    name = "pi"

    def __init__(self,
                 bin_path: str = "pi",
                 stall_timeout_ms: int = 1_800_000,
                 mode: str = "json",
                 extra_args: list[str] | None = None) -> None:
        self.bin_path = bin_path
        self.stall_timeout_ms = stall_timeout_ms
        self.mode = mode  # "json" | "simple"
        self.extra_args = extra_args or []

    def spawn(self,
              prompt: str,
              workspace: str,
              max_turns: int) -> SubprocessResult:
        if self.mode == "json":
            return self._spawn_json(prompt, workspace, max_turns)
        return self._spawn_simple(prompt, workspace, max_turns)

    def _spawn_simple(self, prompt: str, workspace: str, max_turns: int) -> SubprocessResult:
        argv = [self.bin_path, *self.extra_args, "-p", prompt]
        env = {"ORCH_WORKSPACE": workspace, "ORCH_MAX_TURNS": str(max_turns)}
        stdout, stderr, exit_code, stalled, duration = self.run_with_stall_detection(
            argv, cwd=workspace,
            stall_timeout_ms=self.stall_timeout_ms,
            env_overrides=env,
        )
        verdict = self.parse_verdict(stdout) if not stalled else "ABORTED_BY_RECONCILIATION"
        return SubprocessResult(
            stdout=stdout, stderr=stderr, exit_code=exit_code,
            verdict=verdict, duration_s=duration, stalled=stalled, turns_used=1,
        )

    def _spawn_json(self, prompt: str, workspace: str, max_turns: int) -> SubprocessResult:
        argv = [self.bin_path, "--mode", "json", *self.extra_args]
        stdin_payload = json.dumps({
            "prompt": prompt,
            "max_turns": max_turns,
            "workspace": workspace,
        }) + "\n"
        env = {"ORCH_WORKSPACE": workspace, "ORCH_MAX_TURNS": str(max_turns)}
        stdout, stderr, exit_code, stalled, duration = self.run_with_stall_detection(
            argv, cwd=workspace, stdin=stdin_payload,
            stall_timeout_ms=self.stall_timeout_ms,
            env_overrides=env,
        )

        verdict = "CONTINUE_EXHAUSTED"
        turns = 0
        content_chunks: list[str] = []
        if stalled:
            verdict = "ABORTED_BY_RECONCILIATION"
        else:
            for line in stdout.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    content_chunks.append(line)
                    continue
                t = obj.get("type")
                if t == "turn_complete":
                    turns += 1
                elif t == "final":
                    v = obj.get("verdict")
                    if v:
                        verdict = v
                if "content" in obj:
                    content_chunks.append(str(obj["content"]))
            # fallback: scan reconstructed content for last-line VERDICT
            if verdict == "CONTINUE_EXHAUSTED":
                verdict = self.parse_verdict("\n".join(content_chunks))

        return SubprocessResult(
            stdout=stdout, stderr=stderr, exit_code=exit_code,
            verdict=verdict, duration_s=duration, stalled=stalled,
            turns_used=max(1, turns),
        )
