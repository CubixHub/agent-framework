---
name: test-on-edit
description: Run only the tests related to the just-edited file (not the full suite). Tight feedback loop — catches regressions in <30 seconds. Wire as part of a hook chain or invoke per-task.
---

# When to use

- Tight feedback loop on a small change.
- Verifying a fix before moving on.
- During TDD: after each red→green cycle.
- Hook chain: invoke from PostToolUse after Edit/Write.

# How to execute

## Step 1 — Find related tests

For an edited source file, locate its test counterparts:

| Convention | Pattern |
|---|---|
| Colocated unit | `same-dir/<basename>.test.<ext>` or `.spec.<ext>` |
| Mirror-tree (Python) | `tests/<same-path>.py` (or `<pkg>/tests/test_<name>.py`) |
| Mirror-tree (Rust) | `tests/<basename>_test.rs` or `#[cfg(test)] mod tests` in-source |
| Import-based | Grep for `from .<module> import` or `require('./<module>')` in test files |

## Step 2 — Run only those tests

| Test framework | Command |
|---|---|
| Vitest | `vitest run path/to/foo.test.ts` |
| Jest | `jest --findRelatedTests path/to/foo.ts` |
| Pytest | `pytest path/to/test_foo.py` |
| Cargo | `cargo test --test foo_test` |
| Go | `go test ./path/to/...` |

If no related test is found, surface that to the user — they may want to write one.

## Step 3 — Report

```
test-on-edit: ran 3 tests (foo.test.ts, foo.integration.test.ts, bar.test.ts).
  PASS: 3
  FAIL: 0
  Duration: 4.2s
```

If any FAIL, halt — don't proceed with more edits until the test is green again.

## Step 4 — On no related tests

Optionally run the smoke suite (project-defined fast test set) as a fallback,
but don't run the full suite (that's the post-merge gate, not the post-edit gate).

# Wiring as a hook

In Claude Code's `.claude/settings.json`:
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          { "type": "command", "command": "bash .agent-os/hooks/post-edit.sh" }
        ]
      }
    ]
  }
}
```

The `post-edit.sh` dispatcher can include test-on-edit as one of its branches
for source files.

# Anti-patterns (refuse)
- Running the FULL test suite on every edit (defeats the tight-loop purpose).
- Skipping test-on-edit because "I'll run them at the end" — at the end, the
  bug is harder to localize.
- Ignoring the no-related-tests signal — that's a coverage gap.
