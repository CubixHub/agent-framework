# Probe-based summary evaluation

Adapted from Factory Research's evaluation methodology. Tests "can the agent
continue the task" not "does the summary look similar to the original".

## The 4 probe types

### Recall
"What was the original problem / error / requirement?"
- A summary that loses this can't bootstrap the next session.

### Artifact
"Which files did we modify, and how did each change?"
- The hardest dimension — most compactors lose this.
- Aim for >2.5/5 on a 5-point scale, with the structured template.

### Continuation
"What is the immediate next step?"
- A summary that loses this forces re-planning from scratch.

### Decision
"What did we decide and why?"
- Decision rationale that's lost gets re-litigated next session.

## Scoring (0-5)

| Score | Meaning |
|---|---|
| 5 | Verbatim or equivalent; perfect retention |
| 4 | Slight rephrasing; meaning intact |
| 3 | Partial; the agent could approximate the answer |
| 2 | Vague; the agent would need to re-derive |
| 1 | Hallucinated detail; misleading |
| 0 | Nothing relevant; complete loss |

## How to run

1. Compress the session as you normally would.
2. Open a fresh agent context with ONLY the summary (no history).
3. Ask each probe. Record the answer.
4. Score it (or have a J1-tier judge score it).

## Pass bar
- Recall ≥ 3.5
- Artifact ≥ 2.5 (this dimension is genuinely hard)
- Continuation ≥ 4
- Decision ≥ 3.5

If you score below these, your summary template is missing something. Update
the structured template and re-summarize.
