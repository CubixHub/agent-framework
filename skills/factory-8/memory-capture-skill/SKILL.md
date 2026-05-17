---
name: memory-capture-skill
description: Skill-form alternative to the `memory-capture.py` hook. Use when hooks are unavailable or when you want explicit categorization help. Captures decisions, learnings, and preferences to the right file.
---

# When to use

- Hook-less CLI session (some Pi or remote setups).
- User says "remember this:" / "for the future:" / "save this:" — but you want
  to ask classification questions before saving.
- Bulk import from chat history into structured memories.

# How to execute

## Step 1 — Identify the memory shape
For each candidate memory, ask three questions:

| Question | Implications |
|---|---|
| Personal vs project? | personal → `~/.agent-os/memories.md`. project → `.agent-os/memories.md`. |
| Preference vs decision vs learning? | preference = personal usually; decision = project + maybe ADR; learning = wiki concept |
| Dated context relevant? | yes → include date; no → format as ongoing rule |

## Step 2 — Format

```markdown
- [YYYY-MM-DD] <statement>; <one-line rationale>; (ADR: [[adr-NNN-slug]] if any)
```

Be concrete. Not "we use Zustand" — say "We chose Zustand over Redux for client
state (ADR-005); reason: simpler boilerplate."

## Step 3 — Append

Append (never overwrite) to the right file. Order is chronological, newest at
the bottom.

## Step 4 — Cross-link

If the memory is a decision with broader implications:
- Add an ADR at `wiki/plan/adr/adr-NNN-<slug>.md`.
- Link memory → ADR.

If the memory is a learning that's reusable knowledge:
- Add a wiki concept page.
- Link memory → concept page.

## Step 5 — Confirm

Tell the user:
```
✓ Saved to <file>. Cross-linked to <ADR / concept page> if any.
```

# vs the hook

The `.agent-os/hooks/memory-capture.py` does steps 2-3 automatically when the
user starts a message with `#` or `##`. This skill is for the times you want:
- Cross-linking (the hook doesn't do step 4).
- Explicit categorization (the hook makes a guess from prefix only).
- Bulk import from a chat history (the hook is one-at-a-time).

# Anti-patterns (refuse)
- Saving "we should..." statements that are aspirational rather than decisions.
- Saving things that already live in code or rules (read-derived, not declarative).
- Saving without the date.
- Editing an existing memory entry — append a correction instead.
