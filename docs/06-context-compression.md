# Context Compression

> Applies to: Claude Code, Codex, Pi. Summary of Factory Research's *Evaluating Context Compression* post + how the Framework operationalizes it. The shorter version: **measure tokens per task, not tokens per request, and use a probe-based eval to compare compression strategies**.

## Why compression matters

Long sessions hit two walls:

1. **The context window** — eventually the conversation does not fit.
2. **The cost-per-turn curve** — even when it fits, every turn re-pays the context cost. Past a certain length, more context starts to *degrade* quality (the "lost in the middle" effect) as well as run up the bill.

Compression is the operation that takes a long history and replaces it with a shorter representation that preserves the parts the agent will actually need next.

## Tokens-per-task, not tokens-per-request

The wrong metric: "how many tokens did this turn use?" Compressing aggressively wins this metric while sometimes losing the task.

The right metric: "how many total tokens did it take to finish the task?" An aggressive compression that drops a key fact forces the agent to re-derive it (or worse, get it wrong), and the total cost goes up.

When comparing two compression strategies, run them against the same task batch and compare *task completion cost*, not per-turn savings.

## Probe-based evaluation

Compression quality is evaluated against four probe families. Each probe takes a long original history, applies the candidate compression, then queries the compressed result. PASS = the compressed history answers as well as the original.

| Probe | What it tests | Example |
|-------|---------------|---------|
| **Recall** | Specific facts survive | "What was the package name we chose for the auth module in turn 14?" |
| **Artifact** | Generated outputs are reconstructable | "Reproduce the ADR-007 frontmatter exactly." |
| **Continuation** | The agent can pick up from a compressed history | "Resume the refactor we started. Next step?" |
| **Decision** | Reasoning chains are preserved | "We considered Postgres vs SQLite. Why did we pick the choice we picked?" |

A compression strategy is "good" when it passes all four families at acceptable rates on representative tasks. A strategy that wins on Recall but loses on Decision is unusable for planning sessions.

## Compression approaches

### 1. Anchored iterative summarization (preferred)

The Framework's chosen approach. Maintain a single structured summary file (`.agent-os/context.md`) with anchored sections that the agent rewrites in place as the session progresses. Sections are stable; content updates.

```markdown
# Context (compressed)

## Task
<the current task; rewritten as the task narrows>

## Decisions made
- <bullet, with timestamp and reasoning anchor>
- ...

## Open questions
- ...

## Files touched
- src/auth/login.ts — refactored handleLogin
- ...

## Don'ts (learned from failures)
- ...
```

The agent reads `.agent-os/context.md` at session start and updates it at session end (or at compaction checkpoints). The file is committed to the repo — it becomes part of the project's history.

### 2. OpenAI `/responses/compact`

OpenAI's Responses API exposes `responses.compact` which compresses a thread server-side and returns a continuation handle. Fast and zero-effort, but opaque: the agent can't introspect *what* was kept vs dropped. Use when the session is throwaway.

### 3. Anthropic SDK compaction

The Anthropic Messages API supports an explicit "compact" message that signals a summarization checkpoint; Claude returns a continuation summary you reuse in subsequent turns. More transparent than OpenAI's, but still ephemeral — when the session ends, the summary is gone unless you save it.

## The Framework's choice

**Anchored iterative summarization in `.agent-os/context.md`.** Three reasons:

1. **Persistent.** Survives session boundaries; committed to git; reviewable in PRs.
2. **Auditable.** A human can read what the agent thinks the state is. Drift is visible.
3. **Multi-CLI portable.** Same file format read by Claude Code, Codex, Pi. No vendor lock-in.

The SDK-level compaction (OpenAI / Anthropic) is used *within* a single Claude Code or Codex session to keep context manageable mid-session. The anchored summary is what survives between sessions.

## Probe-eval cadence

For projects where compression quality matters (long-running missions, multi-day sessions), run the probe eval monthly:

1. Pick 5 historical sessions of varying length and complexity.
2. Apply each candidate compression.
3. Run the four probe families.
4. Record pass rates per family per strategy.
5. If pass rates drop on the chosen strategy, the strategy is drifting — investigate.

The eval itself lives in `skills/compression-eval/SKILL.md`.

## Compaction triggers

When to compact mid-session:

- Context utilization > 70% of the model's window
- A natural task boundary (just finished a feature; about to start the next)
- After a long debugging detour that ended in a fix — keep the fix, drop the detour

The agent invokes the `context-compression` skill at these points. See `skills/context-compression/SKILL.md` for the runnable procedure: read recent history → write anchored summary → confirm with user → continue.

## What never gets compressed

Some content is canonical and must survive verbatim:

- ADR bodies (live in `wiki/plan/adr/`)
- Memory entries (live in `.agent-os/memories.md`)
- Rule bodies (live in `.agent-os/rules/`)
- Wiki source claims (live in `wiki/sources/`)
- Verification verdicts (live wherever the orchestration daemon writes them)

These are the agent's persistent memory. The compression layer summarizes the *path through* them, not the artifacts themselves.

## Cross-references

- `skills/context-compression/SKILL.md` — the runnable compaction procedure
- `skills/compression-eval/SKILL.md` — the probe-based eval
- [Token efficiency](./05-token-efficiency.md) — the broader cost story compression sits inside
- Factory Research's *Evaluating Context Compression* — original post; this doc adapts its method to the tri-platform setup
