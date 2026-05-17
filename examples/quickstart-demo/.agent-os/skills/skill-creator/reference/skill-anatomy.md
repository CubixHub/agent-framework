# Skill Anatomy

What separates a good skill from a useless one. Read this before authoring.

## The two-tier disclosure model

A skill has two visibility tiers:

| Tier | File | Read | Purpose |
|---|---|---|---|
| Tier 0 | `SKILL.md` frontmatter | On every task (for relevance scoring) | Decide whether to invoke |
| Tier 1 | `SKILL.md` body | When invoked | The action — what to do |
| Tier 2 | `reference/*.md` | On demand, when SKILL.md links to it | Depth, examples, formal specs |

This is progressive disclosure. The frontmatter sells the skill. The body executes it. The reference deepens it. If your skill puts a formal schema in the body, you have inverted the model and burned tokens.

## Description is everything

The agent picks skills by relevance-scoring the `description` field. Everything else is invisible at selection time. Therefore:

- The description is sales copy. It must tell the agent — in one paragraph — exactly when this skill applies.
- Keywords matter: the user's natural phrasing of the task ("test", "debug", "lint") should appear literally if possible.
- Triggers must be concrete: "when user mentions X" beats "when relevant".

See `frontmatter-spec.md` for the formal rules.

## Rigid vs flexible skills

Two valid shapes. Pick consciously.

### Rigid

Use for processes with a single correct sequence. The skill is an ordered checklist; deviation is a bug.

Examples: TDD, security review, deploy procedures.

Shape:

- Numbered steps, in mandatory order.
- Each step has a single deliverable.
- "Done" criteria are exhaustive (every box must be checked).

### Flexible

Use for creative / exploratory work where the path varies but the structure does not.

Examples: brainstorming, architecture exploration, prompt design.

Shape:

- A short set of prompts or questions that bound the exploration.
- A required output shape (what the agent must produce), without dictating the path.
- Anti-patterns to refuse (what NOT to do, even if it seems easier).

**Do not mix shapes.** A "do these 5 steps in any order" skill is a rigid skill written badly. A "freely explore, but here is the order" skill is a flexible skill written badly.

## The five required sections of a SKILL.md body

1. **When to use** — concrete triggers. 4–8 bullets.
2. **How to execute** — the procedure. Numbered for rigid, structured for flexible.
3. **Quality bar** — what "done" looks like. A checklist.
4. **Anti-patterns** — at least 3 specific failure modes the skill refuses.
5. **Reference** — links to `reference/*.md`.

Sections may be combined for short skills, but none may be omitted. A skill without an anti-patterns section is a skill that will be misused — the anti-patterns are how the agent knows what the skill is NOT.

## Reference folder pattern

Every skill ships a `reference/` subdirectory. Minimum: one file. Common files:

- `examples.md` — 2–4 worked examples. Show the input and output, with commentary.
- `<topic>-spec.md` — a formal schema, contract, or rubric.
- `anti-patterns.md` — extended bad-example catalog with reasons.
- `decision-tree.md` — flowchart when the skill branches.

Reference material is the place for verbose content (long examples, formal specs, citation-heavy explanations). The SKILL.md body stays lean.

## Tone

The same tone used in `.factory/rules/general.md`:

- **Imperative.** "Do X." not "Consider X."
- **Opinionated.** State the preferred approach. Hedging is the enemy.
- **Terse.** Every sentence earns its place. Cut adjectives.
- **No hedging language** ("might want to", "you could try", "in some cases"). Either it is mandatory or it is not in the skill.

## Length budget

| Section | Target | Hard cap |
|---|---|---|
| Frontmatter | 4–6 lines | — |
| When to use | 6–12 lines | 20 |
| How to execute | 30–80 lines | 150 |
| Quality bar | 5–10 lines | 20 |
| Anti-patterns | 6–12 lines | 20 |
| Reference (links) | 3–8 lines | — |
| **Total SKILL.md** | 120–250 lines | 300 |

Over budget? Move content to `reference/`.
