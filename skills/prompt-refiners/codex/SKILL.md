---
name: codex-prompt-refiner
description: Rewrite a prompt to follow the Codex/GPT pattern — role framing, numbered procedural steps, explicit chain-of-thought trigger, schema-anchored output
---

# When to use

Target is any GPT/OpenAI/Codex model: GPT-4/5, o-series, Codex, OpenAI Assistants, github.com/openai/codex. Apply when:
- A prompt works on Claude but not on GPT.
- The model "skips steps" or rushes to an answer.
- Output schema is inconsistent.

# How to execute

1. Open with role framing. `You are a <role>` is not flair — it conditions output style and reasoning depth. The role should be specific (`senior backend engineer auditing payment code`), not generic (`helpful assistant`).
2. State the task as numbered procedural steps. GPT models follow numbered lists more reliably than prose paragraphs.
3. Trigger reasoning explicitly. `Think step by step.` or `Let's reason through this carefully.` Especially for o-series, which uses thinking tokens; under-cued, it answers too fast.
4. Specify output schema. For JSON output, give the exact schema. For prose, give the exact section headings.
5. Add few-shot examples ONLY if format is unusual. GPT trained on far more prose-formatted examples than Claude; pure prose examples often help less than format hints.
6. Re-check: numbered steps are atomic (one action per step) and ordered (no "do A then B in parallel with C").

# The Codex/GPT pattern (canonical structure)

```
You are a {{role}}.

Your task: {{one-sentence task}}

Follow these steps:
1. {{atomic step}}
2. {{atomic step}}
3. ...
N. Return the result in the format below.

Constraints:
- {{constraint 1}}
- {{constraint 2}}

Output format:
```json
{
  "field": "schema description",
  ...
}
```

Examples:
Input: {{...}}
Output: {{...}}

Think step by step before producing the final answer.
```

# Worked transformation

## Before (vague)

```
Extract structured data from this support ticket.
```

## After (Codex pattern)

```
You are a senior data engineer extracting structured fields from unstructured support tickets.

Your task: read a support ticket and emit a JSON object with the schema below.

Follow these steps:
1. Read the ticket end-to-end before extracting anything.
2. Identify the customer's primary complaint in ≤15 words.
3. Identify the product area mentioned (one of: billing, auth, api, ui, other).
4. Identify the severity signal (low / medium / high / critical) using the rubric in the constraints section.
5. List the specific error messages or codes verbatim if present.
6. Return the JSON object.

Constraints:
- Severity rubric:
  - critical: production down, data loss, security incident
  - high: degraded function affecting many users
  - medium: workaround exists
  - low: cosmetic or one-off
- If a field is not derivable from the ticket, use null. Do not invent values.

Output format:
```json
{
  "complaint": "string, ≤15 words",
  "product_area": "billing|auth|api|ui|other",
  "severity": "low|medium|high|critical",
  "error_codes": ["string", ...]
}
```

Example:
Input: "Our API has been returning 500s on /v2/charge since this morning. We're losing customers. Already 200+ failed calls."
Output:
```json
{
  "complaint": "API /v2/charge returns 500s; losing customers",
  "product_area": "api",
  "severity": "critical",
  "error_codes": ["500"]
}
```

Think step by step before producing the final answer.
```

# When to skip the pattern

- A trivial single-turn lookup ("what's 2+2").
- A free-form creative task where structure constrains.

# Differences from Claude pattern

| Dimension | Claude | Codex/GPT |
|---|---|---|
| Structure | XML tags | Numbered steps + sections |
| Role | Optional, often skipped | Critical, lead with it |
| Reasoning | `<thinking>` block | "step by step" |
| Examples | Dedicated `<examples>` block, 2 is best | Few-shot inline, 1-3 |
| Output format | Section-tagged | Schema-tagged (JSON block) |

# Anti-patterns

- "Helpful assistant" role. Too generic; useless.
- Prose paragraphs instead of numbered steps for procedures. GPT under-orders.
- Skipping the step-by-step trigger on o-series. Burns reasoning budget without using it.
- Multiple output formats listed as "or either". Pick one.

# Reference

- OpenAI prompt engineering guide
- OpenAI o1 / o-series reasoning best practices
- Sibling: `claude/SKILL.md` for the Claude pattern comparison
