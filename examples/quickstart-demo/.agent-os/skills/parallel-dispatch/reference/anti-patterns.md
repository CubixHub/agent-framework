# Parallel Dispatch Anti-Patterns

Six patterns the lead agent will reach for. Each produces unusable output. Refuse each.

## 1. Dispatch without explicit chunking rules

```
Sub-agent prompt:
  "Write the full SKILL.md for the typescript-types skill. ~800 lines."
```

**What happens.** Sub-agent hits the ~8K output cap mid-file. Truncated output. Lead reads it, sees `<!-- END -->` missing, has to manually finish the file. Worse: lead might not notice the truncation and commit the partial file.

**Why agents reach for it.** Chunking instructions feel verbose to type. The prompt looks "cleaner" without them.

**Fix.** Every dispatch prompt includes the chunking block verbatim. Verbose-but-correct beats clean-but-broken.

## 2. Overlapping file targets

```
Sub-agent A: write to /path/index.md (sections 1–3)
Sub-agent B: write to /path/index.md (sections 4–6)
```

**What happens.** Whichever finishes last wins; the other's output is lost. Or, with race conditions, both partial writes interleave and produce garbage.

**Why agents reach for it.** Splitting one big file feels like the natural decomposition.

**Fix.** Each sub-agent owns one or more **whole** files. If a file's sections are independent, make them separate files. If they can't be split, the lead writes the file directly using Edit-append.

## 3. Sub-agents commit / push

```
Sub-agent prompt:
  "Write the files, then git commit and push."
```

**What happens.** Three sub-agents commit in parallel. Branch is now garbage with three rapid-fire commits, possibly out of order, possibly with conflicts if any file overlaps (see #2). Push amplifies the damage to the remote.

**Why agents reach for it.** Bundling commit into the sub-agent feels efficient.

**Fix.** Sub-agents write files only. The lead reads every sub-agent's output, runs lint, then commits ONCE with a single conventional-commit message naming the dispatch.

## 4. Sequential dispatch (one message per agent)

```
Message 1: dispatch agent A → wait for return
Message 2: dispatch agent B → wait for return
Message 3: dispatch agent C → wait for return
```

**What happens.** No parallelism. Total time = sum of latencies, not max. Defeats the purpose of dispatch. Often slower than the lead writing all three files directly.

**Why agents reach for it.** Mental model is sequential; one-call-per-message is the lazy default.

**Fix.** Dispatch all sub-agents in ONE message with multiple Agent tool calls. The runtime parallelises only batched calls.

## 5. Lead dispatches and walks away

```
Lead: "Dispatched 6 agents. Task complete."
```

**What happens.** No inventory check. No lint. No commit. No audit-log entry. The files exist on disk but nothing has verified they are correct, consistent, or complete. Future sessions inherit silent garbage.

**Why agents reach for it.** Dispatch feels like the work; synthesis feels like overhead.

**Fix.** The lead's job is dispatch AND synthesis. The synthesis step is non-optional. Inventory, lint, log, commit — in that order.

## 6. Dispatching architectural decisions

```
Sub-agent prompt:
  "Decide whether to use Postgres or DynamoDB for the event store. Write the ADR."
```

**What happens.** Three sub-agents return three different answers, each plausible, none coordinated with the rest of the architecture. The "winning" decision becomes whoever's output the lead reads first.

**Why agents reach for it.** Decisions feel like parallelisable work.

**Fix.** The lead makes architectural decisions. Sub-agents flesh out their consequences in writing — that is parallelisable. The pattern is: lead writes the ADR (or at least the Decision + Rationale sections), sub-agents write per-package Consequences sections in parallel.

---

## How to recognise the dodge in flight

Each anti-pattern has a recognisable thought-shape:

- #1: "I'll skip the chunking rules to save space."
- #2: "I can split the file in half between two agents."
- #3: "I'll include 'commit when done' in the sub-agent prompt for efficiency."
- #4: "Let me dispatch one and see what comes back before doing the others."
- #5: "Files landed. We're done."
- #6: "I'll farm out the decision to a sub-agent that can think more deeply."

When you catch any of these thoughts, stop and re-plan. The dispatch is not ready.
