---
name: claude-prompt-refiner
description: Rewrite a prompt to follow the Claude pattern — XML tag structure, dedicated examples section, explicit reasoning triggers, exact output format
---

# When to use

Target is any Claude model: Sonnet, Opus, Haiku, Claude Code, claude.ai. Apply when:
- A prompt works on GPT but not on Claude.
- A prompt is "soft" — vague intent, no structure, no examples.
- Output is inconsistent across runs.

# How to execute

1. Parse the source prompt into 5 buckets: context, task, requirements, constraints, examples. Some buckets may be empty.
2. Rewrite using XML tags. Claude is trained heavily on XML-tagged prompts; tags improve adherence more than any other format.
3. Move examples to a dedicated `<examples>` block AFTER `<task>`. Two examples is the sweet spot; one is fragile, four+ adds noise.
4. If reasoning is needed, explicitly invite it. Use `Think through this in a <thinking>...</thinking> block before responding.` or just `think step by step`. Do not skip — Claude under-uses CoT without invitation.
5. State the output format precisely. If JSON, give the exact schema. If markdown, give the exact section headings.
6. Re-check: every requirement appears at most once. Duplication signals confusion.

# The Claude pattern (canonical structure)

```xml
<context>
Background the model needs to know. Stable across runs.
Project name, tech stack, user persona, dataset shape.
</context>

<task>
The single thing you want the model to do, in one sentence.
Then expand in 2-4 bullets.
</task>

<requirements>
- Hard requirements (must be satisfied)
- Numbered or bulleted
- One per line
</requirements>

<constraints>
- What NOT to do
- Output length, tone, what to avoid
</constraints>

<examples>
<example>
<input>...</input>
<output>...</output>
</example>
<example>
<input>...</input>
<output>...</output>
</example>
</examples>

<output_format>
Exact shape. JSON schema, markdown sections, or "respond with only..."
</output_format>

Think through this in a <thinking> block before producing the final output.
```

# Worked transformation

## Before (vague, GPT-style)

```
You are an expert engineer. Write a function that takes a list and removes duplicates while preserving order. Use Python.
```

## After (Claude pattern)

```xml
<context>
We are writing a small Python utility library used in a data pipeline. Functions in this library are imported and called millions of times per day. Performance matters; readability matters more.
</context>

<task>
Write a Python function `dedupe_preserve_order(items)` that returns a new list with duplicate elements removed, preserving the order of first occurrence.
</task>

<requirements>
- Pure function (no side effects)
- Handles unhashable items by falling back to O(n^2) compare
- Type hints on the signature
- Docstring with one example
</requirements>

<constraints>
- No external dependencies
- No comments inside the function body (the docstring is enough)
</constraints>

<examples>
<example>
<input>[1, 2, 2, 3, 1]</input>
<output>[1, 2, 3]</output>
</example>
<example>
<input>["a", "b", "a", "c"]</input>
<output>["a", "b", "c"]</output>
</example>
</examples>

<output_format>
Return ONLY the Python code, in a single fenced block, no surrounding prose.
</output_format>
```

# When to skip the pattern

- The prompt is already <10 words and the task is trivial ("translate to French: ...").
- You're inside an agentic loop and brevity matters more than structure.

# Anti-patterns

- Wrapping everything in `<instruction>` only — Claude responds to semantic tags. Use `<context>` for context, not `<instruction>`.
- Examples before task. Examples teach format; the task statement frames intent.
- Forgetting `<output_format>`. Claude will choose a format and it may not be yours.
- "Be creative" + strict format. Pick one.

# Reference

- Anthropic prompt engineering guide
- Claude system prompt examples (Anthropic cookbook)
- Sibling: `codex/SKILL.md` for the GPT pattern comparison
