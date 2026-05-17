---
name: ai-engineering
description: Index for the five end-to-end AI engineering sub-skills — design, train, finetune, deploy, eval — with a decision tree for which one to invoke
---

# When to use

User asks anything about building, training, fine-tuning, deploying, or evaluating a model — pick the right sub-skill from the decision tree. Do not freelance.

# Decision tree

```
User wants to:
├── Pick architecture / size / data budget / tokenizer        → model-design/
├── Run a pretrain or continued-pretrain                       → model-training/
├── Adapt a model with SFT / DPO / RLHF / LoRA                → model-finetuning/
├── Serve a model behind an inference engine                  → model-deployment/
└── Score a model on benchmarks / build custom evals          → model-evaluation/
```

Combinations:
- "Build a domain model from scratch" → design → training → evaluation → deployment
- "Adapt Llama-3 for our use case" → finetuning → evaluation → deployment
- "Replace OpenAI with self-hosted" → deployment → evaluation
- "Our model is dumb at X" → evaluation first, then finetuning

# How to execute

1. Read the matched sub-skill's SKILL.md end-to-end.
2. Open the wiki and check for prior decisions in `concepts/` and ADRs touching the same area. Cite them or supersede them — never silently diverge.
3. Produce the sub-skill's required output artifact (design doc, training run plan, finetune recipe, deployment manifest, eval report).
4. File findings back to the wiki as `concepts/<topic>.md` with frontmatter and source citations.

# Required outputs by sub-skill

| Sub-skill | Required artifact |
|---|---|
| model-design | `design-doc.md` with architecture/size/data/tokenizer/compute rationale |
| model-training | Training run plan with framework, parallelism, MFU target, checkpoints, eval-in-loop hooks |
| model-finetuning | Recipe spec (method, dataset, hyperparams, eval gates, catastrophic-forgetting guard) |
| model-deployment | Manifest (engine, quantization, batching, KV mgmt, serving framework, observability) |
| model-evaluation | Eval report (benchmarks + custom + contamination check + judge tier used) |

# Cross-skill rules

- Never train without an eval-in-loop hook. A loss curve alone is not signal.
- Never deploy without a quantization-vs-quality eval. Quantization without measurement is gambling.
- Never finetune without a held-out test that includes pre-training capabilities — catch catastrophic forgetting.
- The model that generated an artifact must not grade it. Use a different model family for evals.

# Reference

- Chinchilla scaling: ~20 tokens per parameter for compute-optimal pretrain
- MFU baseline: >40% is healthy on H100 with FSDP+bf16; <30% means a config bug
- LoRA target: rank 8–64, alpha = 2× rank, dropout 0.05; merge before serving unless you need multi-tenant adapters
- Inference engines as of 2026: vLLM (default), SGLang (highest throughput), TensorRT-LLM (NVIDIA-only max perf), llama.cpp (CPU/edge)
- Judge stack: tier J0→J4 from `skills/verification-first/`
