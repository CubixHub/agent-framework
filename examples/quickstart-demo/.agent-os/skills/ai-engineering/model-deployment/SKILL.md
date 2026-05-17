---
name: model-deployment
description: Serve a model in production — inference engine, quantization, batching, KV cache, speculative decoding, multi-GPU TP/PP, multi-tenant adapters, serving framework, observability
---

# When to use

User says any of: "serve model X", "deploy to production", "pick inference engine", "quantize for serving", "max throughput", "self-host", "replace OpenAI". A model-evaluation/ run on the unquantized base is a prerequisite — without it you can't measure quantization quality loss.

# How to execute

1. Lock SLOs. Latency budget (p50, p99), throughput (tokens/sec), concurrency, accuracy floor, cost ceiling. Refuse to design without all five.
2. Pick the inference engine by target (table below).
3. Pick quantization by accuracy budget. Run quantization eval against the unquantized baseline — never deploy without this measurement.
4. Decide batching mode: continuous batching (default for chat), static batching only for fixed-shape pipelines, streaming for token-by-token UIs.
5. Plan KV cache: budget memory per concurrent user × max-context. Enable PagedAttention (vLLM/SGLang) for non-trivial concurrency.
6. Plan parallelism: tensor-parallel (TP) within a node, pipeline-parallel (PP) across nodes only when single-node TP is infeasible. TP=2,4,8 are common; avoid TP=3 (matmul alignment penalties).
7. Add speculative decoding if cost-sensitive. Draft model 7-30x smaller than target. Expect 1.5-3x speedup on most workloads.
8. Pick serving framework (table below). Don't write a serving framework yourself.
9. Wire observability: latency histograms (TTFT, ITL), tokens-in/tokens-out, GPU util, KV cache fill, queue depth, eviction count, OOM counter.
10. Load-test with realistic prompts BEFORE production traffic. Use real prompt-distribution from logs, not synthetic.

# Inference engine pick (as of 2026)

| Goal | Pick | Why |
|---|---|---|
| Default OSS production | vLLM | Continuous batching, PagedAttention, mature |
| Highest throughput, complex sampling | SGLang | RadixAttention, structured outputs, fastest on most benchmarks |
| Max NVIDIA perf, willing to compile | TensorRT-LLM | 1.5-2x vs vLLM, painful build |
| HuggingFace ecosystem, simple | TGI | Easiest setup |
| CPU/edge/laptop | llama.cpp + GGUF | Quantized, CPU-friendly, Apple Silicon |
| Multi-tenant LoRA | vLLM (multi-LoRA) or SGLang | Both support adapter swapping |

# Quantization pick

| Target | Method | Quality loss |
|---|---|---|
| 50% memory, minimal quality loss | AWQ (W4A16) | ~0.5-1 pt on MMLU |
| 50% memory, faster than AWQ | GPTQ (W4A16) | ~0.5-1.5 pt on MMLU |
| Max throughput on H100/H200 | FP8 (W8A8) | <0.5 pt on MMLU |
| Aggressive memory savings | INT4 + per-group scaling | 1-3 pt on MMLU, dangerous |
| KV cache shrink | FP8 KV cache | Negligible quality loss |

Rule: always benchmark on YOUR eval set, not the marketing claim. Reasoning capabilities degrade faster than fact recall.

# Serving framework pick

| Need | Pick |
|---|---|
| Pure inference, k8s-native | Ray Serve or BentoML |
| Multi-model, multi-modality | Triton Inference Server |
| Simple HTTP + autoscale | BentoML or LitServe |
| Embedded in app | vLLM/SGLang as a library |

# Multi-GPU pattern

| Model size + GPUs | Layout |
|---|---|
| <30B, 1×H100 | Single-GPU, no parallelism |
| 30-70B, 2-4×H100 | TP=2 or TP=4 |
| 70B+, 8×H100 single node | TP=8 |
| 200B+ | TP=8 within node, PP across nodes |
| MoE (DeepSeek-V3, Qwen-MoE) | Expert parallelism (EP), not TP — SGLang strongly preferred |

# Observability

Required metrics:
- TTFT (time-to-first-token) p50/p95/p99
- ITL (inter-token latency) p50/p95/p99
- Throughput (output tokens/sec, system-wide)
- GPU memory used, KV cache utilization
- Queue depth, request eviction count
- Per-tenant tokens-billed (if multi-tenant)

# Anti-patterns

- Deploying quantized without an eval delta vs unquantized.
- Static batching for chat (kills latency under load).
- Speculative decoding with draft >50% of target size (no speedup).
- Custom serving stack. Always reuse vLLM/SGLang/TRT-LLM.
- Ignoring KV cache memory in capacity planning. KV often dominates over weights at high concurrency.

# Reference

- vLLM docs · SGLang paper · TensorRT-LLM perf guide
- AWQ paper · GPTQ paper · FP8 in Transformer Engine
- PagedAttention paper (vLLM) · RadixAttention (SGLang)
- Speculative decoding (Leviathan et al.)
