---
name: deep-research
description: Multi-step research with a fixed tool-call budget — decompose question into parallel subquestions, fan out research-subagents, synthesize with mandatory source citation, surface contradictions
---

# When to use

Trigger phrases: "research X", "what's the state of Y", "compare A vs B", "deep dive on Z", "due diligence", "best practices for", "literature review". Also trigger when the user asks anything that requires >3 source pages OR cross-cuts >2 wiki categories.

Do NOT trigger for: simple lookups (a single page answers it), code edits, or planning tasks where the answer is already known.

# How to execute

1. **Observe**: read the question carefully. Restate it. Identify what makes it hard — breadth, depth, conflicting evidence, novelty.
2. **Orient**: scan `wiki/index.md` and `wiki/sources/`. Has this been researched already? If yes, cite + extend; do not duplicate.
3. **Decide**: produce 3-7 subquestions. Each must be answerable independently (no shared state). Set a tool-call budget per subquestion (default 10).
4. **Act**: fan out research-subagents (one per subquestion). See `reference/research-subagent-prompt.md` for the canonical prompt. Each subagent runs OODA locally with its budget.
5. **Synthesize**: collect all subagent outputs. Resolve contradictions explicitly — do not paper over them. See `reference/methodology.md` for the tree-of-thought variant.
6. **Cite**: every non-trivial claim ends with a wikilink to a source page. See `reference/source-citation-format.md`.
7. **File back**: write the synthesis to `wiki/questions/<slug>.md` with frontmatter. Update `wiki/index.md`. Append to `wiki/log.md`.

# The OODA loop

Used at TWO levels: the lead (steps 1-4 above) AND each subagent (in its own task).

| Step | At lead | At subagent |
|---|---|---|
| Observe | Read question, scan wiki | Read assignment, scan budget |
| Orient | Identify decomposition shape | Pick first source / search query |
| Decide | Pick subquestions + budgets | Pick next action within budget |
| Act | Dispatch subagents | WebFetch / WebSearch / Read |

Re-loop after each Act. Stop when budget exhausted OR answer-confidence threshold met.

# Tool-call budget

Default per subagent: 10 (5 search + 5 fetch + 0 slack). Adjust by complexity:
- Shallow (factual lookup): 3-5
- Medium (compare 2-3 things): 8-12
- Deep (state-of-art survey): 15-25

Refuse open-ended research without a budget. Unbounded research = drifting research.

# Source citation rule

EVERY non-trivial claim has an inline citation. Format:
```
Claim. [[sources/2025-paper-name]]
```

A claim without a citation is unsupported and must be marked `<!-- UNCITED -->` or removed.

# Surface contradictions

When sources disagree:
```
> ⚠ Source A says X. Source B says Y. As of YYYY-MM-DD:
> - X is supported by [[sources/...]]
> - Y is supported by [[sources/...]]
> Unresolved. <one-sentence implication for the question>
```

Never silently pick a side. Contradictions are signal.

# Output artifact

`wiki/questions/<slug>.md` with frontmatter:
```yaml
---
title: <human question>
type: question
tags: [research, ...]
updated: YYYY-MM-DD
sources: [list of wikilinks to source pages]
---
```

Body sections: question · scope · key findings (3-7 bullets, each cited) · contradictions surfaced · what's uncertain · next-research IDs.

# Anti-patterns

- Skipping the wiki scan. You re-derive what's already there.
- Asking a subagent "do everything." Decompose first.
- Open-ended budget. Subagents drift; lead loses control.
- Uncited claims. Wiki rot starts here.
- Resolving contradictions silently. You're hiding the most important data.

# Reference

- `reference/methodology.md` — tree-of-thought variant
- `reference/research-lead-prompt.md` — copy-paste lead prompt
- `reference/research-subagent-prompt.md` — copy-paste subagent prompt
- `reference/source-citation-format.md` — exact citation format
