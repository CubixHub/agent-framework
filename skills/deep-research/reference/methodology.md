# Deep-Research Methodology — Tree-of-Thought Variant

A constrained tree-of-thought for research. Branching by subquestion (not by hypothesis). Pruning by relevance. Convergence by source saturation.

## The tree

```
Q (root question)
├── SQ-1 (subquestion 1)
│   ├── Source A
│   ├── Source B
│   └── Synthesis-1
├── SQ-2
│   ├── Source C
│   └── Synthesis-2
└── SQ-N
    └── ...
```

Root and leaf both produce structured outputs. The tree is bounded — typically 3-7 SQs, 2-5 sources each.

## Branching rules

When generating subquestions, each must satisfy:

1. **Independent**: answerable without waiting on a sibling.
2. **Falsifiable**: there exists evidence that would change the answer.
3. **Bounded**: a sub-budget can be drawn around it.
4. **Non-overlapping**: two subquestions should not both need source X for the same reason. If they do, hoist X to the parent.

If the user asks "compare A vs B for use case U", canonical decomposition is:
- SQ-1: What does A do well for U? evidence?
- SQ-2: What does B do well for U? evidence?
- SQ-3: Where do A and B disagree on U?
- SQ-4: Are there third options the question elides?
- SQ-5: What's the consensus / state-of-the-art as of `<date>`?

## Pruning rules

A subquestion is PRUNED when:
- Its budget is exhausted AND confidence is high enough — stop, synthesize.
- The lead encounters a meta-result that makes the SQ moot (e.g., one option is deprecated since a published date).
- Two SQs converge to the same source set — merge.

A subquestion is EXPANDED (new child SQs created) when:
- Sources disagree non-trivially — spawn a child SQ to dig into why.
- A source surfaces a new dimension the original SQs missed.

## Convergence criterion

Stop when ANY of:
1. **Source saturation**: 3+ independent sources agree, no new sources contradict within last 2 searches.
2. **Budget exhaustion**: tool-call budget consumed (report incomplete with what's missing).
3. **Confidence threshold**: lead can answer the original question with cited evidence at >0.8 confidence.
4. **Time cap**: wall-clock budget hit (be honest about partial results).

## Synthesis rules

The lead synthesizes by:
1. Reading every subagent's output in full.
2. Building the **claim ledger**: every claim with its supporting source(s) and contradicting source(s).
3. For each claim: classify as `consensus` / `disputed` / `single-source-only` / `inferred`.
4. Surface ALL disputed claims with `⚠` callouts. Never pick a side silently.
5. State explicitly what the research did NOT cover. Open questions become future-research IDs.

## Anti-patterns

- Adding a 4th level of nesting. Almost never helps; usually adds noise.
- Letting one SQ consume the budget of others — enforce per-SQ caps.
- Synthesis that omits contradictions ("on balance, X seems true") without naming the sources that contradict X.
- Inferring beyond evidence. Mark inferences `<!-- INFERRED -->`.

## Reference

- Tree-of-Thought paper (Yao et al., 2023)
- Anthropic research on multi-agent research agents
- OODA loop (Boyd) for the per-iteration decision cycle
