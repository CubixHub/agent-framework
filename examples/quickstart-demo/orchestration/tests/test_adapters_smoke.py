"""Smoke tests for CLI adapters — mock the subprocess.

Asserts that the verdict-parsing envelope works for:
  - Claude adapter (last-line VERDICT)
  - Codex adapter (last-line VERDICT)
  - Pi JSON adapter (final-object verdict)
  - Fallback when no VERDICT line is present -> CONTINUE_EXHAUSTED
"""
from __future__ import annotations

from unittest import mock

from orchestration.adapters.base import CLIAdapter, SubprocessResult
from orchestration.adapters.claude_adapter import ClaudeAdapter
from orchestration.adapters.codex_adapter import CodexAdapter
from orchestration.adapters.pi_adapter import PiAdapter


def _patch(cls, stdout, exit_code=0, stalled=False, duration=0.1, stderr=""):
    return mock.patch.object(
        cls, "run_with_stall_detection",
        return_value=(stdout, stderr, exit_code, stalled, duration),
    )


def test_parse_verdict_last_line():
    out = "log line\nanother\nVERDICT: PASS\n"
    assert CLIAdapter.parse_verdict(out) == "PASS"


def test_parse_verdict_with_bullet_prefix():
    out = "foo\n> VERDICT: NEEDS_HUMAN\n"
    assert CLIAdapter.parse_verdict(out) == "NEEDS_HUMAN"


def test_parse_verdict_no_match_returns_continue_exhausted():
    assert CLIAdapter.parse_verdict("nothing here\n") == "CONTINUE_EXHAUSTED"


def test_claude_adapter_pass():
    a = ClaudeAdapter(bin_path="claude")
    with _patch(ClaudeAdapter, "ok\nVERDICT: PASS\n"):
        r = a.spawn("p", "/tmp", max_turns=3)
    assert r.verdict == "PASS"
    assert r.exit_code == 0
    assert isinstance(r, SubprocessResult)


def test_claude_adapter_stall_aborts():
    a = ClaudeAdapter(bin_path="claude")
    with _patch(ClaudeAdapter, "partial", stalled=True, exit_code=-9):
        r = a.spawn("p", "/tmp", max_turns=3)
    assert r.stalled is True
    assert r.verdict == "ABORTED_BY_RECONCILIATION"


def test_codex_adapter_proxy_pass():
    a = CodexAdapter(bin_path="codex")
    with _patch(CodexAdapter, "doing things\nVERDICT: PROXY_PASS\n"):
        r = a.spawn("p", "/tmp", max_turns=3)
    assert r.verdict == "PROXY_PASS"


def test_pi_adapter_json_final_verdict():
    lines = "\n".join([
        '{"type":"thinking","content":"thinking..."}',
        '{"type":"tool_use","content":"ls"}',
        '{"type":"turn_complete","content":"end-of-turn"}',
        '{"type":"final","verdict":"PASS","content":"done"}',
    ]) + "\n"
    a = PiAdapter(bin_path="pi", mode="json")
    with _patch(PiAdapter, lines):
        r = a.spawn("p", "/tmp", max_turns=3)
    assert r.verdict == "PASS"
    assert r.turns_used >= 1


def test_pi_adapter_json_fallback_to_text_verdict():
    """If pi doesn't emit a `final` object, fall back to last-line parse."""
    lines = (
        '{"type":"turn_complete","content":"VERDICT: NEEDS_HUMAN"}\n'
    )
    a = PiAdapter(bin_path="pi", mode="json")
    with _patch(PiAdapter, lines):
        r = a.spawn("p", "/tmp", max_turns=3)
    assert r.verdict == "NEEDS_HUMAN"


def test_pi_adapter_simple_mode():
    a = PiAdapter(bin_path="pi", mode="simple")
    with _patch(PiAdapter, "stuff\nVERDICT: FAIL\n"):
        r = a.spawn("p", "/tmp", max_turns=3)
    assert r.verdict == "FAIL"
