---
name: model-finetuning
description: Adapt a pretrained model with SFT, DPO, ORPO, RLHF/RLAIF, or LoRA/QLoRA — including dataset prep, framework choice, eval gates, catastrophic-forgetting watch, and merge-vs-adapter decision
---

# When to use

User says any of: "fine-tune", "adapt model X", "SFT on our data", "preference tuning", "RLHF", "LoRA", "instruction-tune", "domain-tune". Never finetune without a model-evaluation/ baseline first — you need a before-after delta.

# How to execute

1. Get the baseline. Run `model-evaluation/` on the pretrained model with your target eval set. If you skip this you cannot prove the finetune helped.
2. Pick the method by data shape (table below).
3. Prep the dataset. Quality dominates quantity for SFT. For preference data, ensure pairs are real preferences (not synthetic rejections of identical generations).
4. Pick framework by method + scale (table below).
5. Pick LoRA vs full-finetune. LoRA when: <1M tokens of data, you need multi-tenant adapters, or you cannot afford full-finetune compute. Full when: >10M tokens, single deployed model, behavior change is large.
6. Set hyperparams. LR 100x lower than pretrain (typically 1e-5 to 1e-6 for full, 1e-4 to 5e-4 for LoRA). Epochs: 1–3 for SFT, 1–2 for DPO.
7. Wire eval-at-every-checkpoint. Include BOTH your target eval AND a pretraining-capabilities eval (HellaSwag, MMLU, ARC) — if pretraining capabilities drop >2 points, catastrophic forgetting is happening.
8. Run. Watch for: loss collapse, eval divergence, reward hacking (DPO/RLHF), KL explosion (RLHF).
9. Decide merge-vs-adapter. Merge LoRA weights for production serving unless you need multi-tenant. Keep adapter for experimentation.
10. Final eval. Demand a 2-judge cross-check (J1 + J3 from verification-first stack).

# Method pick

| Data shape | Method | Why |
|---|---|---|
| `(prompt, response)` pairs | SFT | Cheapest, most common starting point |
| `(prompt, chosen, rejected)` pairs | DPO | RLHF-quality without reward model |
| `(prompt, chosen, rejected)` w/ no reference model | ORPO | Single-stage; no SFT prereq |
| `(prompt, response, reward)` with online sampling | RLHF (PPO/GRPO) | When you have a reward model worth using |
| `(prompt, response)` w/ AI-graded reward | RLAIF | When human labelers are bottleneck |

Rule of thumb: do SFT first, then DPO/ORPO on the SFT model. Skip RLHF unless you have a strong reward model and infrastructure to do it.

# Framework pick

| Method + scale | Framework |
|---|---|
| SFT/DPO, <13B, fast iteration | TRL (HF) or Unsloth (2-5x speedup) |
| SFT/DPO, recipe-first, 7–70B | Axolotl |
| SFT/DPO with curriculum, multi-stage | LLaMA-Factory |
| Full RLHF/GRPO | TRL or veRL |
| Long-context SFT (>32k) | Unsloth or Axolotl with FlashAttention-3 |

# Dataset prep

- SFT: dedup, length filter, response-quality filter, prompt-variety check. 5–50k high-quality > 500k mediocre.
- Preference (DPO): real pairs only. Filter pairs where chosen == rejected. Score margin distribution should be non-degenerate.
- Instruction-tuning: cover task-type, length, and language distribution. Use the recipe from FLAN or T0 as a sanity check.

# Catastrophic-forgetting watch

Track pretraining benchmarks at every eval point:
- MMLU drop >2 points → reduce LR, reduce epochs
- HumanEval drop >5 points → coding ability collapsing; rebalance dataset
- IFEval drop → instruction-following decaying; add general-instruction data

# Merge vs adapter

| Goal | Choice |
|---|---|
| Single fixed deployment | Merge LoRA + serve |
| Multi-tenant w/ per-customer adapters | Keep adapters, serve via vLLM/SGLang multi-LoRA |
| Adapter stacking | Keep adapters |
| Maximum throughput | Merge |

# Anti-patterns

- Finetuning without a baseline.
- LoRA rank 256 because "bigger is better" — usually rank 8–32 is optimal; high rank overfits and slows.
- DPO without SFT. DPO assumes a competent base; cold DPO is unstable.
- Skipping pretraining-capabilities eval. You'll ship a worse model than you started with.
- Self-grading: using the finetune model to grade itself. Use a different family.

# Reference

- TRL docs · Axolotl recipes repo · Unsloth notebooks
- DPO paper (Rafailov et al.) · ORPO paper · GRPO (DeepSeek)
- LoRA paper · QLoRA paper for 4-bit base
