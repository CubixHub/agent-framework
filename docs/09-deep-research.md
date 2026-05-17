# Deep Research Workflow

> Applies to: Claude Code, Codex, Pi. When a question is bigger than a web search but smaller than a project, use the deep-research workflow. Inspired by Weizhena/Deep-Research-skills.

## When to use deep research vs quick web search

| Question shape | Tool |
|----------------|------|
| "What's the syntax for X?" | Quick web search |
| "What changed in v3 of Y?" | Quick web search + release notes |
| "Why does Y deprecate the X pattern?" | Quick web search; one paragraph synthesis |
| "What's the best library for X given constraints A, B, C?" | **Deep research** |
| "How do five teams operate Y?" | **Deep research** |
| "Is approach A better than approach B for our context?" | **Deep research** |
| "State of the art for X in 2026?" | **Deep research** |

Heuristic: if the answer is "it depends, and you need to investigate the deps", it's deep research.

## Multi-agent research coalition

The coalition has three roles. The agent invoking this skill is the **lead**.

```
       Lead (coordinator, synthesizer)
        │
   ┌────┴────┬────────┬────────┐
   ▼         ▼        ▼        ▼
 Sub-1     Sub-2    Sub-3    Sub-N      (parallel exploration)
 (branch)  (branch) (branch) (branch)
   │         │        │        │
   └────┬────┴────────┴────────┘
        ▼
       Synthesizer (lead reads all sub-findings → produces report)
```

### Lead

- Owns the OODA budget (see below).
- Decomposes the question into 2–6 branches.
- Dispatches sub-agents in parallel.
- Synthesizes their findings into a single report.
- Files the report to `wiki/questions/<slug>.md` and `wiki/sources/<slug>.md` if new sources were ingested.

### Sub-agents

- One per branch.
- Have their own tool-call budget (a slice of the lead's).
- Return a structured findings JSON: claims, sources, contradictions, confidence.
- **Cite every non-trivial claim** with a URL or wiki source path.

### Synthesizer

- Same agent as lead (one less context switch).
- Reads sub-findings; merges; surfaces contradictions explicitly.
- Produces a report ≤ 2 pages with a verdict and confidence rating.

## OODA loop with tool-call budget

Each branch runs an Observe-Orient-Decide-Act loop with a hard tool-call budget. When the budget is exhausted, the branch terminates and returns whatever it has.

| Phase | Tools the branch may use | Budget cap |
|-------|--------------------------|------------|
| Observe | Web search, fetch URL, read existing wiki | 40% of budget |
| Orient | Synthesize what's been read; identify gaps | 0 tool calls (in-context reasoning) |
| Decide | Choose next 1–3 fetches | 0 tool calls |
| Act | Execute the fetches | 60% of budget |

Typical budgets:

- Shallow research (single branch, 5 min): 5 tool calls
- Medium (3 branches, 15 min): 30 tool calls (10/branch)
- Deep (5 branches, 45 min): 100 tool calls (20/branch)

If a branch hits the budget mid-investigation, it returns "partial — needs more budget to resolve <gap>". The lead decides whether to extend.

## Source citation discipline

Every non-trivial claim in the report links to a source. Two formats:

```
<claim> [<source-slug>]
<claim> ([<source-slug>], [<other-source-slug>])
```

`<source-slug>` is the filename (without `.md`) in `wiki/sources/`. If the source is brand new from this research, the lead writes the source card as part of the synthesis step — the report should never reference a source that doesn't have a wiki card.

When sources contradict each other, surface explicitly:

```markdown
> ⚠ [[sources/vendor-a-2026-05]] contradicts [[sources/vendor-b-2026-04]]
> on X. Vendor A claims Y; Vendor B claims Z. <one-sentence on resolution>.
```

Never silently pick a winner.

## Wiki integration — file findings back

Every research session ends with two wiki writes:

1. **`wiki/questions/<slug>.md`** — the question + the report. Frontmatter `type: question`. This is the answer the next agent will find when querying the wiki.
2. **`wiki/sources/<slug>.md`** for each newly-ingested source — bibliographic card with URL, retrieval date, key claims.

Plus an entry in `wiki/log.md`:

```
2026-05-17  research  +wiki/questions/x.md  "Comparative analysis of X vs Y"
```

If you don't file findings, the research is wasted — the next agent re-derives the answer.

## Worked examples

### Example: comparative analysis

> Question: "Should we use Linear or Plane for the orchestration daemon's PM tool?"

Branches:
1. Feature comparison (state machine, labels, API)
2. Pricing / hosting (cost vs self-host)
3. API ergonomics (rate limits, webhook quality)
4. Agent-friendliness (which fits the daemon's poll/claim/comment pattern)

Sub-agents in parallel; ~15 min total. Synthesizer produces a recommendation matrix. See [PM tool choice](./11-pm-tool-choice.md) for the resulting doc.

### Example: due diligence

> Question: "Is Pi (pi.dev) stable enough to ship as a primary worker CLI alongside Claude Code and Codex?"

Branches:
1. Repo activity (commits, contributors, release cadence)
2. Feature coverage (compare against Claude Code feature list)
3. Production users (case studies, GitHub orgs depending on it)
4. Failure modes (open issues, common pitfalls)

Sub-agents in parallel; ~30 min total. Report files to `wiki/questions/pi-stability-assessment.md`.

### Example: state-of-the-art survey

> Question: "What's the state of the art for context compression as of 2026-05?"

Branches:
1. Paper survey (Factory Research, arXiv, vendor research blogs)
2. Vendor SDK approaches (OpenAI, Anthropic, others)
3. Open-source implementations
4. Probe evaluations (how teams measure)

See [Context compression](./06-context-compression.md) for the resulting doc.

## Triggering the workflow

- **Claude Code**: invoke the `deep-research` skill: `Skill({ skill: "deep-research", args: "<question>" })`. The skill body dispatches sub-agents.
- **Codex**: invoke the skill by reference: "Using deep-research skill to answer: <question>". Codex reads `skills/deep-research/SKILL.md` and dispatches.
- **Pi**: `pi install @framework/deep-research` then invoke. The Pi extension exposes a tool that drives the OODA loop.

The Borg MCP `hive_mind_research` tool is one implementation of this pattern, with Gemini + Opus + Codex as the three agents. Use it when available; otherwise the per-CLI skill dispatches sub-agents through the CLI's own sub-agent surface.

## Cross-references

- `skills/deep-research/SKILL.md` — the runnable procedure
- `skills/llm-wiki/SKILL.md` — the wiki file-back at end of session
- [Context compression](./06-context-compression.md) — what to do with the long history this generates
- Weizhena/Deep-Research-skills — the inspiration repo
