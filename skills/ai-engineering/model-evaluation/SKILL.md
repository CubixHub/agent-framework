---
name: model-evaluation
description: Score a model on public benchmarks AND build custom rubric/pairwise evals — with contamination check, LLM-judge tier choice, anti-gaming primitives, and behavioural fingerprinting
---

# When to use

User says any of: "evaluate model X", "benchmark", "is the model good at Y", "compare A vs B", "regression suite", "build evals", "score this finetune". Run this BEFORE finetuning (baseline) and AFTER (delta). Never skip the contamination check.

# How to execute

1. Define what "good" means in writing. Single-number metric is a trap — list the dimensions (correctness, format adherence, refusal calibration, latency, cost).
2. Pick the public benchmark battery (table below). Run on a clean evaluation harness (lm-eval-harness or simple-evals), not custom code.
3. Build custom evals for capabilities the public benchmarks miss. Choose grading mode: deterministic (regex/exec/schema) > pairwise > rubric.
4. Run contamination check on the candidate model: N-gram overlap of benchmark questions against training data, OR check known leak benchmarks (e.g., RealityCheck, contamination kit).
5. Pick the judge tier (J0-J4 from verification-first/) by cost budget. Default: J0 for deterministic, J1 for online, J3 for spot-check, J4 for version comparisons.
6. Anti-gaming: snapshot the eval files before any run, restore before grading. Compare claimed outputs vs actual outputs. Break the code intentionally and verify your evals catch it (mutation test).
7. Run behavioural fingerprinting on candidate vs baseline: same prompts, compare outputs token-by-token. Surface drift even when scores match.
8. Write the eval report. Include: per-benchmark scores with confidence intervals, custom-eval scores, contamination findings, judge tier used, fingerprint delta.
9. File `concepts/<model>-eval.md` to the wiki. Future you needs this for regression comparisons.

# Public benchmark battery

| Capability | Benchmark | Notes |
|---|---|---|
| General knowledge | MMLU, MMLU-Pro | MMLU-Pro is harder; MMLU is contaminated by 2026 |
| Code generation | HumanEval, MBPP, LiveCodeBench | LiveCodeBench is contamination-resistant (rolling) |
| Math reasoning | GSM8K, MATH, AIME | AIME is the high bar; GSM8K is saturated |
| Instruction following | IFEval | Format / constraint adherence |
| Multi-turn chat | MT-Bench (judged), Chatbot Arena (Elo) | Elo > MT-Bench for production signal |
| Long context | RULER, LongBench, NIAH | NIAH is necessary-not-sufficient |
| Tool use | BFCL, ToolBench | BFCL is the standard |
| Safety | HarmBench, JailbreakBench | If you ship to users |

# Custom evals — grading mode pick

| Mode | When |
|---|---|
| Deterministic (J0) | Output is parseable: JSON, code, regex match, exec test, schema validate |
| Pairwise (J3/J4) | Comparing two model versions; absolute score not needed |
| Rubric (J1/J2) | Open-ended quality; provide 3-5 dimensions, score each 1-5 |
| A/B production | Real user signal; only with consent |

# Anti-gaming primitives (mandatory)

| | Rule | Why |
|---|---|---|
| AG-1 | Snapshot eval files before run; restore before grading | "I modified the eval to pass" |
| AG-2 | Diff claimed outputs vs actual responses | "I lied about what the model said" |
| AG-3 | Break the model intentionally (corrupt weights) and verify evals FAIL | No-real-tests tautology |
| AG-4 | Combine programmatic check + judgement on every assertion | UI-text-only judges miss server-state bugs |

# Contamination check

For every public benchmark you report:
1. Compute 13-gram overlap between benchmark items and any disclosed pretrain dataset.
2. Run a "memorization probe": ask the model to continue the first 50 tokens of a benchmark question; if it produces the gold answer verbatim, contamination is near-certain.
3. Report contamination findings WITH the score. A 90% MMLU score with 30% contamination is a 60% effective score.

# Behavioural fingerprinting

- Fixed prompt suite (50-200 diverse prompts).
- Run candidate + baseline at temp=0.
- Diff outputs token-by-token. Compute: edit distance, semantic similarity, response-length delta, refusal-rate delta.
- Surface deltas >threshold even when benchmark scores match. Catches regressions the benchmarks miss.

# Eval report artifact

Required sections: scope · model under test · baseline · public benchmark scores w/ CI · custom eval scores · contamination report · judge tier · fingerprint delta · pass/fail verdict per dimension · open questions.

# Anti-patterns

- Single-number eval ("model X is 85"). Always multi-dimensional.
- Reporting benchmark scores without contamination check. Default-suspicious in 2026.
- Self-judging (same model grades itself). Always cross-family.
- Cherry-picking benchmarks where model wins. Pre-register the battery.
- Skipping behavioural fingerprinting between versions. You'll ship a regression.

# Reference

- HELM · lm-evaluation-harness · simple-evals (OpenAI) · evalplus
- LMSYS Chatbot Arena · MT-Bench paper
- LiveCodeBench, BFCL, IFEval papers
- Contamination kit / RealityCheck papers
- Verification-first skill for judge-tier definitions
