# Source Citation Format

Every non-trivial claim cites a source page in the wiki. The wiki page in turn cites the upstream URL/file. This makes the wiki the spine of accountability.

## Inline citation

Default format — wikilink to a source page:
```
The DPO loss outperforms PPO on preference benchmarks in 6/7 settings. [[sources/dpo-paper-2023]]
```

If the source is brand-new and a source page does not yet exist, use a TODO marker:
```
SGLang's RadixAttention reduces TTFT by 30-40% vs vLLM under shared-prefix workloads. [[sources/sglang-paper-2024]] <!-- TODO: file source -->
```

Then file the source page as a follow-up before the research is considered complete.

## What counts as "non-trivial"

A claim that:
- Asserts a fact a reader might want to verify, OR
- Compares two things by a measurable property, OR
- Reports a benchmark or experimental result, OR
- Names a technique, paper, or person and attributes a property to them.

A claim that does NOT need citation:
- Restatement of the question.
- Definitions taken as given in the immediate context.
- Pure logical inference made explicit (mark `<!-- INFERRED -->`).

## Source page format

`wiki/sources/<slug>.md`:
```yaml
---
title: <Source title>
type: source
tags: [paper | blog | doc | talk | dataset, <topic-tags>]
updated: YYYY-MM-DD
authors: [list]
year: NNNN
url: https://...
local: raw/<filename> (if mirrored)
---

# <Source title>

## Why this matters
<2-4 sentences>

## Key claims
1. <claim>. <page or section ref>
2. ...

## Related concepts
[[concepts/...]] [[concepts/...]]

## Related entities
[[entities/...]] [[entities/...]]

## Limitations / caveats
- ...
```

## Multi-source citations

When a claim needs >1 source (consensus signal):
```
Speculative decoding gives 1.5-3x speedup on typical workloads. [[sources/spec-dec-paper-2023]] [[sources/vllm-spec-dec-blog]]
```

## Disputed-claim format

When claims conflict, do NOT pick a side. Use the callout:
```
> ⚠ Source A claims TP=8 is optimal for 70B on H100 [[sources/a]]; Source B reports TP=4 + sequence parallel wins [[sources/b]]. As of 2026-03-01 this is unresolved at the hardware/workload combination of <X>.
```

## What NOT to do

- Citing only the URL without filing a source page. Future you can't audit.
- Citing the wiki page itself for a claim that originates upstream. Cite the upstream page.
- Hiding a contradiction inside a footnote. Surface it in the body.
- Loose citation ("as is well known"). Either cite or remove.

## Reference

- Wikipedia's citation policy as a baseline for "non-trivial"
- Wiki schema: `skills/llm-wiki/reference/wiki-schema.md`
