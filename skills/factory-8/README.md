# Factory 8 — agent-skills toolkit

Eight skills rewritten from Factory.ai's skills guide for tri-CLI (Claude / Codex / Pi).
Each one is independently usable. Cross-references go to the Framework's own
versions of related skills where applicable.

## The 8

1. **[readiness-report](readiness-report/SKILL.md)** — Audit a project's AI-readiness; rank gaps; emit fixable punch-list.
2. **[spec-mode](spec-mode/SKILL.md)** — Plan-before-code for non-trivial tasks. The cross-CLI Spec Mode pattern.
3. **[context-aware-implementation](context-aware-implementation/SKILL.md)** — Read memories + rules + wiki BEFORE implementing.
4. **[prompt-refiner-team](prompt-refiner-team/SKILL.md)** — Team-tuned prompt refiner that applies the project's own conventions.
5. **[memory-capture-skill](memory-capture-skill/SKILL.md)** — Skill-form alternative to the memory-capture hook.
6. **[token-aware-implementation](token-aware-implementation/SKILL.md)** — Implement with token budget in mind; model-tier dispatch.
7. **[auto-format-on-edit](auto-format-on-edit/SKILL.md)** — Skill-form alternative to the format-on-edit hook.
8. **[test-on-edit](test-on-edit/SKILL.md)** — Run only the tests related to the just-edited file.

## How these relate to the Framework's own skills

| Factory-8 skill | Framework primary skill |
|---|---|
| readiness-report | (standalone; not duplicated) |
| spec-mode | [../brainstorming/](../brainstorming/SKILL.md) is the lead-in |
| context-aware-implementation | uses [../llm-wiki/](../llm-wiki/SKILL.md) |
| prompt-refiner-team | composes with [../prompt-refiners/](../prompt-refiners/) per-CLI ones |
| memory-capture-skill | parallel to `.agent-os/hooks/memory-capture.py` |
| token-aware-implementation | uses ../../docs/05-token-efficiency.md |
| auto-format-on-edit | parallel to `.agent-os/hooks/format-on-edit.sh` |
| test-on-edit | parallel to `.agent-os/hooks/post-edit.sh` dispatcher |

## Attribution
Concepts adapted from https://docs.factory.ai/guides/skills/. Translation
to tri-CLI is the Framework's responsibility.
