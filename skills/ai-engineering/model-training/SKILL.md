---
name: model-training
description: Execute a pretrain or continued-pretrain — framework choice, parallelism, mixed precision, data pipeline, checkpointing, eval-in-loop, MFU monitoring, crash recovery
---

# When to use

User says any of: "pretrain", "train from scratch", "continued pretrain", "extend context window via training", "run a long training job". A finished `model-design/` design doc is a prerequisite — refuse to start without one.

# How to execute

1. Confirm the design doc is signed off. No design doc → go back to `model-design/`.
2. Pick the training framework by scale. Stack below.
3. Stand up the data pipeline FIRST. Test it end-to-end with a 1B-token mini-run before launching the real run. Data-loader bugs are the most common cause of silent training corruption.
4. Configure parallelism: tensor parallel (TP) for the largest matmuls, pipeline parallel (PP) for >1-node, FSDP/ZeRO-3 for parameter sharding. Use 2D or 3D parallelism only when you must — debugging is brutal.
5. Set mixed precision: bf16 for everything by default. FP8 only on H100/H200 with a known-good recipe (Transformer Engine). Never use fp16 for pretrain — loss-scale instability burns runs.
6. Wire eval-in-loop: run a fixed validation set every N steps AND run a downstream eval (HellaSwag / MMLU-tiny) every M steps. Train loss alone hides regressions.
7. Wire Wandb (or equivalent). Log: loss, grad norm, LR, MFU, tokens/sec, samples-per-step, GPU mem, NaN counter.
8. Set checkpoint cadence: every 1B tokens or every hour, whichever is more frequent. Keep last 3 + every 10th. Test checkpoint reload BEFORE the real run.
9. Define the crash-recovery playbook before launch (template below).
10. Launch. Watch the first 1B tokens like a hawk — most catastrophes happen in the first hour.

# Framework pick

| Scale | Framework | Why |
|---|---|---|
| <8B, single node | PyTorch FSDP | Lowest overhead, native torch |
| 7–70B, 1–8 nodes | DeepSpeed ZeRO-3 or FSDP | Mature, well-documented |
| 30B–500B, 8+ nodes | Megatron-LM (or Megatron-DeepSpeed) | 3D parallelism, TP/PP fused kernels |
| MoE or research | Composer (MosaicML) | Best ergonomics for new techniques |

# Data pipeline

| Scale | Tool |
|---|---|
| <100B tokens | WebDataset or HuggingFace datasets streaming |
| >100B tokens, multi-node | MosaicML Streaming (S3/GCS deterministic shards) |
| Frontier (T+) | Megatron data loader with pre-tokenized binary shards |

Always: deterministic shuffle seed, document-attention boundaries set, dedup before shard creation, token-count sanity check before launch.

# MFU target

Healthy MFU on H100 with FSDP + bf16:
- 8B: 45–55%
- 70B: 40–50%
- MoE: 30–45% active-MFU

<30% = config bug. Re-check: micro-batch size, sequence parallel, compiled attention (FlashAttention-3), pinned memory, NCCL config.

# Cluster ops

| Setup | Orchestrator |
|---|---|
| Bare metal HPC | Slurm |
| Cloud burst | Ray + Anyscale or Skypilot |
| K8s shop | Kubeflow / Volcano / Ray-on-K8s |

Mandatory: NCCL_DEBUG=INFO at launch, persistent storage for checkpoints decoupled from compute nodes, dead-node detection + auto-resume.

# Crash-recovery playbook

1. Last good checkpoint identified within 60 seconds of crash.
2. Detect cause (OOM / NaN / hardware / NCCL).
3. Re-launch with same seed and same step count. Verify loss matches pre-crash curve within 1%.
4. If loss diverges: roll back further, the checkpoint was corrupted.

# Anti-patterns

- Launching without a data-loader unit test.
- fp16 mixed precision on a fresh recipe.
- No downstream eval in the loop — your loss is dropping and your model is getting dumber.
- Checkpointing only at the end. One hardware fault and you lose a week.
- Tuning LR after the run starts. Pick LR via mu-transfer or known scaling laws BEFORE launch.

# Reference

- DeepSpeed ZeRO paper · Megatron-LM paper · FSDP docs
- MosaicML Composer + Streaming
- FlashAttention-3 for H100 throughput
- mu-Parametrization (Yang et al.) for transferring LR across sizes
