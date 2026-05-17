"""Abstract base for coding-CLI adapters (Claude / Codex / Pi).

CONTRACT (every concrete adapter MUST honor this):

  spawn(prompt, workspace, max_turns) -> SubprocessResult

  - Spawn the CLI as a subprocess in `workspace` cwd.
  - Pass `prompt` via -p flag (or stdin for json-mode adapters).
  - Capture stdout + stderr line-by-line; detect stall if neither
    stream produces output for `stall_timeout_ms` (default 30 min).
  - The LAST stdout line MUST match the regex
    ^VERDICT:\\s*(PASS|PROXY_PASS|FAIL|NEEDS_HUMAN|CONTINUE|HUMAN_APPROVAL_REQUIRED)\\b
    Capture the verdict; if no match, record verdict="CONTINUE_EXHAUSTED"
    so the runner can route to Failed.
  - Multi-turn semantics: max_turns controls how many continuation
    rounds the adapter will permit (claude: --continue; codex: --turns;
    pi: turn loop in JSON mode). After exhaustion, force
    verdict="CONTINUE_EXHAUSTED".

JSON envelope (Pi only — see pi_adapter.py for full schema):
  Each stdout line is a JSON object with keys:
    type:    "turn_complete"|"thinking"|"tool_use"|"final"
    verdict: present on type=final
    content: free-form payload
"""
from __future__ import annotations

import os
import re
import select
import subprocess
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

VERDICT_RX = re.compile(
    r"^VERDICT:\s*(PASS|PROXY_PASS|FAIL|NEEDS_HUMAN|CONTINUE|HUMAN_APPROVAL_REQUIRED)\b"
)


@dataclass
class SubprocessResult:
    stdout: str
    stderr: str
    exit_code: int
    verdict: str                  # one of the seven verdicts, or CONTINUE_EXHAUSTED
    duration_s: float
    turns_used: int = 1
    stalled: bool = False
    extra: dict = field(default_factory=dict)


class CLIAdapter(ABC):
    """Subclass and implement `spawn()`. Use helpers below for stall + parse."""

    name: str = "base"

    @abstractmethod
    def spawn(self, prompt: str, workspace: str, max_turns: int) -> SubprocessResult:
        ...

    # ---------- shared helpers ----------

    @staticmethod
    def parse_verdict(stdout: str) -> str:
        """Walk the stdout from the bottom looking for the verdict line."""
        for line in reversed(stdout.splitlines()):
            line = line.strip()
            if not line:
                continue
            m = VERDICT_RX.match(line)
            if m:
                return m.group(1)
            # also accept verdict embedded as first token after stripping
            # leading bullets/quotes/etc.
            stripped = line.lstrip("`>*- \t\"'")
            m = VERDICT_RX.match(stripped)
            if m:
                return m.group(1)
        return "CONTINUE_EXHAUSTED"

    @staticmethod
    def run_with_stall_detection(
        argv: list[str],
        *,
        cwd: str,
        stdin: Optional[str] = None,
        stall_timeout_ms: int = 1_800_000,
        env_overrides: Optional[dict] = None,
    ) -> tuple[str, str, int, bool, float]:
        """Run a subprocess; kill if no output for `stall_timeout_ms`.

        Returns (stdout, stderr, exit_code, stalled, duration_s).
        """
        env = os.environ.copy()
        if env_overrides:
            env.update(env_overrides)
        t0 = time.time()
        proc = subprocess.Popen(
            argv, cwd=cwd, env=env,
            stdin=subprocess.PIPE if stdin is not None else None,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, bufsize=1,
        )
        if stdin is not None and proc.stdin:
            try:
                proc.stdin.write(stdin)
                proc.stdin.close()
            except BrokenPipeError:
                pass

        stdout_buf, stderr_buf = [], []
        last_io = time.time()
        stalled = False
        timeout_s = stall_timeout_ms / 1000.0
        try:
            while True:
                if proc.stdout is None or proc.stderr is None:
                    break
                ready, _, _ = select.select(
                    [proc.stdout, proc.stderr], [], [], 1.0
                )
                if ready:
                    for r in ready:
                        chunk = r.readline()
                        if chunk:
                            (stdout_buf if r is proc.stdout else stderr_buf).append(chunk)
                            last_io = time.time()
                if proc.poll() is not None:
                    # drain remaining
                    if proc.stdout:
                        stdout_buf.append(proc.stdout.read() or "")
                    if proc.stderr:
                        stderr_buf.append(proc.stderr.read() or "")
                    break
                if time.time() - last_io > timeout_s:
                    proc.kill()
                    stalled = True
                    break
        except Exception:
            proc.kill()
            raise

        exit_code = proc.wait()
        return "".join(stdout_buf), "".join(stderr_buf), exit_code, stalled, time.time() - t0
