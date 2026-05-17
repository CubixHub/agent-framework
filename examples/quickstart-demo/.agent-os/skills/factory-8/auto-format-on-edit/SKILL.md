---
name: auto-format-on-edit
description: Skill-form alternative to `format-on-edit.sh` hook. For CLIs without hook support, OR when you want format-on-edit per-task rather than per-session. Runs the language-appropriate formatter after every Write or Edit.
---

# When to use

- Hook-less CLI sessions.
- Single-task formatting (don't want session-wide formatting hook).
- When the project's formatter has special flags (e.g. `prettier --plugin-foo`).

# How to execute

## Step 1 — Detect file's language

| Extension | Formatter |
|---|---|
| `.ts`, `.tsx`, `.js`, `.jsx`, `.json`, `.md`, `.yaml`, `.yml` | `prettier --write` |
| `.py` | `ruff format` (or `black -q`) |
| `.rs` | `rustfmt` |
| `.go` | `gofmt -w` |
| `.java` | `google-java-format -i` |
| `.kt` | `ktlint -F` |
| `.css`, `.scss` | `prettier --write` |
| `.sql` | `sqlfluff fix` |

## Step 2 — Run after every Write/Edit

For each file the agent writes or edits:
```bash
<formatter> "<file>" >/dev/null 2>&1 || true
```

The `|| true` means: if no formatter is available, exit silently. Don't fail
the session.

## Step 3 — Re-read the file if format changed it

After formatting, the file content may differ from what you wrote. If you're
about to do another Edit on it, Read it first to confirm content.

## Step 4 — Don't block on format failures

If `prettier --write` fails because of a syntax error in the file, that's the
underlying syntax error's fault, not the formatter's. Surface the syntax error
to the user; don't keep retrying the format.

# vs the hook

The `.agent-os/hooks/format-on-edit.sh` does this automatically on PostToolUse.
This skill is for:
- CLIs without hook support.
- Tasks where you want explicit formatter control.
- Bulk format passes (run on a glob of files).

# Anti-patterns (refuse)
- Running a different formatter than the project's chosen one.
- Hard-failing on `prettier` errors — they're usually downstream of syntax.
- Skipping format for "small" edits — small edits accumulate format drift.
