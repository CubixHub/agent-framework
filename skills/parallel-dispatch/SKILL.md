---
name: parallel-dispatch
description: Decompose large work into N parallel sub-agent tasks with strict chunking — master+N pattern, layer-batched, range-batched. Use when the work touches >=4 non-overlapping files, when each output is independently authorable, or when the user explicitly asks to parallelise. Refuses dispatch without a written prompt template and explicit chunking rules.
---

# Parallel Dispatch

Sub-agents are cheap. Token caps per agent are fixed (~8K output). Therefore: large work decomposes into many small agents, each producing one focused artifact, each writing to a non-overlapping target.

The lead agent's job is to (a) decide if dispatch is appropriate, (b) produce explicit prompts for sub-agents, (c) synthesise their outputs.

## When to use

Dispatch is appropriate when ALL of the following hold:

- The work decomposes into ≥3 independent units (separate files, separate concerns).
- Units have no shared mutable state — no sub-agent's output blocks another's.
- The lead agent would otherwise hit its own output cap.
- A clean dispatch-prompt template can be written (see `reference/dispatch-template.md`).

Do NOT dispatch when:

- The work is a single focused doc < 400 lines. Lead writes directly.
- The pieces depend on each other (sub-agent B needs A's output). Sequential, not parallel.
- The work is a deep architectural decision. The lead must think this through; do not externalise.
- The pieces share a file. Multiple writes to the same file = collisions.

# How to execute

## Step 1 — Pick the shape

Three canonical shapes:

| Shape | Use when | Example |
|---|---|---|
| **Master + N** | One overview doc + N deep-dive docs | One `README.md` + N per-package READMEs |
| **Layer-batched** | Work decomposes by architectural layer | Dispatch one agent per layer (L0..L5), each writes its layer's docs |
| **Range-batched** | Work is a numbered series | Dispatch one agent per ID range (BB-001..040, BB-041..080) |

The user's request usually maps to exactly one shape. If you cannot pick, the work is not ready for dispatch.

## Step 2 — Write the dispatch prompt template

Every sub-agent's prompt contains exactly five sections in this order:

1. **What to do** — 1–2 sentences. The task in plain language.
2. **Read first** — explicit absolute paths the sub-agent must read for context (spec docs, existing files).
3. **Files to write** — explicit absolute paths, one per Write call. Include the count.
4. **Per-file content guidance** — 1–2 paragraphs per file. What goes in it.
5. **STRICT RULES** — chunking, ≤120 lines per call, no other files, no git, no commit.
6. **REPORT BACK** — what the sub-agent summarises (paths, line counts, hardest decision, follow-ups).

(That is six numbered sections; section 5 and 6 are both mandatory framing.)

See `reference/dispatch-template.md` for the copy-paste skeleton.

## Step 3 — Chunking rules (mandatory in every sub-agent prompt)

Sub-agents hit output caps (~8K per response). Files over 400 lines MUST be chunked:

1. **Seed Write**: frontmatter + intro + first 1–2 sections (~150 lines max). Include a stable trailing marker like `<!-- END -->`.
2. **Edit-append**: each subsequent section is its own Edit call inserting BEFORE the `<!-- END -->` marker.
3. **Each Write or Edit produces ≤120 lines** of output.
4. **Do not re-read the file between Edit calls.** The runtime tracks state.

These rules go verbatim into every dispatch prompt. The sub-agent that ignores them will produce truncated files.

## Step 4 — Dispatch in a single message

All sub-agents are spawned in **one message** with multiple Agent calls. Never one-by-one. The runtime parallelises only when calls are batched.

```
WRONG:
  Message 1: dispatch agent A → wait → result
  Message 2: dispatch agent B → wait → result

RIGHT:
  Message 1: dispatch agent A, B, C, D simultaneously → wait → all results
```

## Step 5 — Synthesise

After all sub-agents return:

1. Inventory: `find <output-dir> -type f | wc -l`. Confirm count matches expectation.
2. Line counts: `wc -l <files>`. Confirm none truncated (should be close to target).
3. Lint: run the project's broken-link / format / type check. Treat output as punch-list.
4. Log: append to the project's audit log (`wiki/log.md` or equivalent) what was dispatched and what landed.
5. Commit: single conventional-commit message. Sub-agents never commit; lead does.

# Quality bar

- [ ] Shape (master+N / layer / range) picked consciously.
- [ ] Dispatch prompt template followed (6 sections, all present).
- [ ] Sub-agents dispatched in ONE message, not sequentially.
- [ ] Chunking rules included verbatim in every prompt.
- [ ] No file appears as a write target for >1 sub-agent.
- [ ] Sub-agents instructed not to commit, not to git push, not to run lint themselves.
- [ ] Lead synthesised (inventory + lint + log + commit) after returns.

# Anti-patterns

See `reference/anti-patterns.md` for the full six. Quick form:

1. **Dispatch without explicit chunking rules** → truncated files.
2. **Overlapping file targets** → write collisions.
3. **Sub-agents commit / push** → cascading conflicts.
4. **Sequential dispatch** → no parallelism, slower than direct write.
5. **Lead dispatches and walks away** → no synthesis, no lint, no commit.
6. **Dispatching architectural decisions** → fragmented thinking, no coherence.

# Reference

- `reference/dispatch-template.md` — copy-paste sub-agent prompt skeleton.
- `reference/anti-patterns.md` — the six anti-patterns, with reasons.
- PROJECT-TEMPLATE-SPEC.md §9 — the canonical pattern this skill encodes.
