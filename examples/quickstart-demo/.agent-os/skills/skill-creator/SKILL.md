---
name: skill-creator
description: Author a new skill when no existing skill matches the current task. Use when the agent surveys available skills and finds zero with >=30% confidence relevance, when the user asks "make a skill for X", or when a recurring pattern emerges that future tasks will reuse. Produces SKILL.md plus reference/ material under the appropriate skills/ subdirectory.
---

# When to use

Invoke this skill when **any** of the following is true:

- `skill-discovery` ran and returned zero matches above the 30% confidence threshold.
- The user explicitly requests skill creation ("make a skill", "add a skill for X", "this should be a skill").
- A pattern has now occurred 3+ times in this project and you find yourself re-deriving the same approach. The third time, the skill is overdue.
- You are about to do something the framework's existing skills should already cover but do not.

Do **not** invoke when:

- A near-match exists. Improve the existing skill instead.
- The task is a one-off. Skills compound; one-offs do not.

# How to execute

Five steps. Do not skip any.

## Step 1 — Probe existing skills

Before writing anything, list every skill currently available and check for overlap. Skim each `SKILL.md` description. If you find any partial match (any keyword overlap, even loose), pause and ask the user: "Skill X partially covers this. Extend it, or create a new one?" Most "new skill" requests are actually extensions.

```bash
find /home/boldog/Desktop/Framework/skills -name "SKILL.md" -exec head -3 {} \;
```

## Step 2 — Draft frontmatter

The `description` is the single most load-bearing field. The agent picks skills based on this string alone — it is the relevance-score input. Bad description = invisible skill.

Required shape (see `reference/frontmatter-spec.md`):

```yaml
---
name: <kebab-case-slug>
description: <verb> when <trigger 1>, <trigger 2>, or <trigger 3>. <one-line capability summary>.
---
```

Rules for `description`:

- Start with a verb (the action the skill performs).
- Enumerate 2–4 concrete triggers ("when the user…", "when X is detected").
- End with the capability in plain language.
- 1–3 sentences. Longer = unread. Shorter = unmatchable.
- Vague descriptions are the #1 reason skills do not trigger. "Helps with code" is invisible. "Write Vitest unit tests using AAA pattern when user mentions tests or coverage" is selectable.

## Step 3 — Write the SKILL.md body

Four sections, in this order:

1. **When to use** — concrete triggers. The agent reads this to confirm a match.
2. **How to execute** — numbered steps. Imperative voice. "Do X." not "Consider X."
3. **Quality bar** — what "done correctly" looks like. Checklists welcome.
4. **Reference** — links to `reference/*.md` for depth material.

Keep SKILL.md ≤300 lines. Long bodies go to `reference/`. Progressive disclosure: agents read SKILL.md every time; reference material only when needed.

## Step 4 — Write reference/ material

Create a `reference/` subdirectory next to SKILL.md. Each reference file is one focused topic. Common patterns:

- `examples.md` — 2–4 worked examples
- `<topic>-spec.md` — formal schema or contract
- `anti-patterns.md` — what not to do, with reasons

## Step 5 — Register

The framework's `skills/README.md` is the index. Add a one-line entry under the appropriate category (Discovery / Process / Quality / Engineering / Style). Confirm the entry is alphabetised within its section.

# Quality bar

A skill ships only if:

- [ ] Frontmatter has `name` (kebab-case) and `description` (verb + triggers + capability).
- [ ] SKILL.md ≤300 lines.
- [ ] At least one reference/ file exists (depth material).
- [ ] All "do X" statements are imperative (no "consider", no "you might want to").
- [ ] An anti-patterns section names at least 3 specific failure modes.
- [ ] Re-reading the description makes you certain the skill will trigger on the right tasks.

If any box is unchecked, the skill is not ready.

# Examples

See `reference/examples.md` for two worked examples:

- **Rigid** (TDD-style): explicit ordered steps, mandatory checklist.
- **Flexible** (brainstorming): structured prompts, output shape, but freedom in execution.

# Anti-patterns

Refuse to ship a skill that does any of these:

- **Vague description** ("Helps with X", "Assists in Y"). The relevance scorer will skip it.
- **No anti-patterns section**. A skill that doesn't say what to refuse is a skill that will be misused.
- **Mixing two skills**. One skill, one concern. If you wrote two `When to use` blocks, split it.
- **No reference/ folder**. SKILL.md alone is a sketch, not a skill.
- **Restating principles without prescribing steps**. "Tests are good" is not a skill. "Run X before Y" is.
- **Skipping the existing-skill probe** (Step 1). Most new skills are extensions of existing ones.

# Reference

- `reference/frontmatter-spec.md` — canonical schema
- `reference/skill-anatomy.md` — what makes a good skill
- `reference/examples.md` — worked examples
