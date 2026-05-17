# Judge stack — when to use which tier

## J0 — Deterministic graders
- Exit codes, schema validation, regex matches, `==` comparisons.
- Use whenever ground truth exists. Free. Instant.
- Examples: "test exited 0", "JSON matches schema X", "file contains substring Y".

## J1 — Distilled small judge (per rubric)
- Phi-3-mini, Llama-3.1-8B, Mistral-7B finetuned on the rubric.
- Production: every action that needs judgement, not just nightly.
- Cost: $0.0001/call, ~50ms latency.
- Trained from J3 frontier outputs on a calibration set.

## J2 — OS structured judge
- Prometheus 2, Llama-3.1-70B with structured output.
- Batch / nightly evals where J1 might be too small.
- Cost: ~$0.01/call, 1s latency.
- Catches things J1 misses (subtle reasoning errors, multi-hop facts).

## J3 — Frontier spot-check
- Opus, GPT-frontier.
- Use for 1% sampling of production. Quarterly calibration runs.
- Cost: ~$0.10/call, 5s latency.
- Used to retrain J1 on its disagreements.

## J4 — Pairwise + self-consistency
- Two outputs A and B, ask judge "which is better and why."
- Sample 5 judge passes, take majority.
- Use for version comparisons (canary vs control).

## Cost table (illustrative, May 2026)
| Tier | $/call | Latency | Used per day at 1k actions |
|---|---|---|---|
| J0 | $0     | <10ms | $0 |
| J1 | $0.0001 | 50ms | $0.10 |
| J2 | $0.01  | 1s    | $10 (if all calls) — typically batch |
| J3 | $0.10  | 5s    | $1 (1% sample) |
| J4 | $0.50  | 25s   | rare; version cuts only |

## The rule the entire stack enforces
The model that generated the artifact MUST NOT grade it. Use a different model
family or a different size. Empirically: a smaller dedicated grader beats the
generator at grading on both accuracy AND cost.
