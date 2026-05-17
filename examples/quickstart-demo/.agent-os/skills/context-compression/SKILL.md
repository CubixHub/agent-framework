---
name: context-compression
description: Use anchored iterative summarization to compress long agent sessions without losing task-critical state. Optimize tokens-per-task, not tokens-per-request. Update structured summary by merging new spans rather than regenerating the whole thing.
---

# When to use

- Long-running sessions approaching the context limit.
- Resumption: restoring an agent to mid-task state across sessions.
- Cross-CLI handoffs (Claude session → Codex follow-up → Pi finish).
- When you're about to use a vendor compact tool (prefer this skill instead;
  vendor compactors lose more task-critical state).

# How to execute

## The cardinal rule
Optimize **tokens-per-task**, not **tokens-per-request**.

A naive compactor that saves 5% on input cost but loses one fact you'll have to
re-derive costs 10× more in re-fetch + re-reason. Treat the summary as
load-bearing infrastructure.

## Step 1 — Maintain a structured summary at `.agent-os/context.md`
See [reference/structured-summary-template.md](reference/structured-summary-template.md).

Sections (in this order):
1. **Intent** — what the agent is trying to accomplish.
2. **Decisions made** — non-obvious choices and their rationale.
3. **File modifications** — what changed where (path + nature of change).
4. **Open questions** — what's still unresolved.
5. **Next steps** — the immediate todos.

Never regenerate the whole summary from scratch on compression. Always:
- Summarize ONLY the newly-truncated span.
- MERGE the new summary into the existing one, preserving items still relevant.

## Step 2 — Compress only when needed
Don't compress preemptively. Trigger when:
- Context >70% of model limit, OR
- Cross-session resumption, OR
- Cross-CLI handoff.

## Step 3 — Verify with probe questions
See [reference/probe-evaluation.md](reference/probe-evaluation.md).

Before declaring the compressed summary "good", ask the agent 4 probes:
1. **Recall**: "What was the original error?"
2. **Artifact**: "Which files did we modify and how?"
3. **Continuation**: "What should we do next?"
4. **Decision**: "What did we decide and why?"

If any answer is hallucinated, weaken your trust in the summary. Re-summarize.

## Step 4 — Use the wiki for permanent knowledge
Anything that will outlive the current task moves to the wiki (sources/, concepts/,
questions/), not the summary. The summary is for in-flight task state only.

# Reference
- [reference/probe-evaluation.md](reference/probe-evaluation.md)
- [reference/structured-summary-template.md](reference/structured-summary-template.md)

# Anti-patterns (refuse)
- Using vendor `/compact` blindly — it optimizes tokens-per-request, not tokens-per-task.
- Regenerating the full summary on every compress.
- Compressing knowledge that belongs in the wiki.
- Trusting the summary without probe-evaluation.
