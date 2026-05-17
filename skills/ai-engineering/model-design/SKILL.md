---
name: model-design
description: Choose architecture (encoder/decoder/encoder-decoder/MoE), parameter size, data budget, tokenizer, and compute envelope BEFORE writing any training code
---

# When to use

User says any of: "design a model", "what size model", "choose architecture", "what's the compute budget", "tokenizer choice", "pretrain a model for X". Never skip this step before training — design errors compound for the entire training run.

# How to execute

1. Lock the inference target FIRST. Latency budget, memory budget, accuracy floor. Design backwards from this — picking arch before knowing the target is the most common failure.
2. Pick architecture by task shape (table below). Reject vibes-based choices.
3. Compute the Chinchilla-optimal token budget for the candidate size: `tokens = 20 * params`. If your data is below this, drop the size; if you have 10x more data, go bigger.
4. Pick tokenizer based on domain language coverage. Train a fresh BPE/SentencePiece if domain is non-English or has heavy code/symbol content; otherwise reuse Llama-3 or Qwen tokenizer to inherit ecosystem.
5. Compute the compute envelope: `FLOPs ≈ 6 * params * tokens`. Convert to GPU-hours at the target chip's effective FLOPS (use ~40% MFU as planning baseline).
6. Write the design doc artifact (template below). Submit for ADR-style sign-off before any pretrain run is queued.

# Architecture pick

| Task shape | Pick | Why |
|---|---|---|
| Generation / chat / completion | Decoder-only (Llama, Qwen, Mistral) | KV cache friendly; ecosystem dominance |
| Classification / retrieval embedding | Encoder-only (BERT, ModernBERT) | Bidirectional context, no causal mask waste |
| Seq2seq with structured I/O (translation, summarization w/ strict format) | Encoder-decoder (T5, FLAN-T5) | Strong inductive bias for cross-attention |
| Frontier capability + sparse compute | MoE (Mixtral, Qwen-MoE, DeepSeek-V3) | Higher capacity per active-FLOP |

# Size pick

| Active params | Use case | Pretrain tokens (Chinchilla) | Realistic GPU-hours (H100, 40% MFU) |
|---|---|---|---|
| 1–3B | On-device, latency-critical | 20–60B | ~5k–15k |
| 7–8B | General-purpose default | 140–160B | ~30k–60k |
| 13–30B | Reasoning-heavy single-GPU serving | 260B–600B | ~100k–300k |
| 70B | Frontier-class dense | 1.4T+ | ~500k–1M |
| MoE A3B-A22B | Lower-cost frontier capability | 1–15T total | ~200k–800k |

# Tokenizer

- Reuse existing tokenizer if domain matches the source corpus (English+code → Llama-3, multilingual → Qwen, math/code → DeepSeek).
- Train new tokenizer (32k–128k vocab) when domain has heavy non-English text, custom symbols, or niche code dialects. Use SentencePiece BPE. Measure compression ratio vs reuse candidate; <1.10x improvement = not worth ecosystem cost.

# Design doc artifact

Required sections: target inference profile · architecture choice + rationale · size + Chinchilla math · tokenizer choice + compression measurement · compute envelope (FLOPs, GPU-hours, $) · data recipe outline · risks · evaluation plan stub.

# Anti-patterns

- "We'll scale data later." Chinchilla under-trained models never recover.
- Picking 70B before knowing if you can serve it. Serve-side TP/PP and KV memory bind hard.
- Brand-new tokenizer because "it'll be better." Almost always worse than reusing; you forfeit eval ecosystem.

# Reference

- Chinchilla scaling (Hoffmann et al.): 20 tokens/param compute-optimal
- DeepSeek-V3 technical report for MoE design choices
- Modern BERT (2024) for encoder-only revival
- 6 * params * tokens approximation: Kaplan et al.
