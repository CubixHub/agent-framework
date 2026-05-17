---
name: prompt-refiner-team
description: Refine prompts using this team's conventions and project context. Composes with the per-CLI prompt-refiners (claude/codex/pi). Invoke before sending complex tasks to a sub-agent or external consultant.
---

# When to use

- Dispatching a sub-agent for a complex task.
- Sending a question to a cross-CLI consultant (codex-consultant from Claude lead, etc.).
- Filing a Linear/Plane issue that will be picked up by the orchestration daemon.
- Before any "long-tail" prompt the user expects high-quality output from.

# How to execute

## Step 1 — Identify the target audience
- Which CLI will execute? → load the matching prompt-refiner skill:
  - Claude → `prompt-refiners/claude/SKILL.md` (XML tags pattern).
  - Codex → `prompt-refiners/codex/SKILL.md` (role-framing pattern).
  - Pi → `prompt-refiners/pi/SKILL.md` (SYSTEM.md + capability-packages pattern).

## Step 2 — Layer team-specific context

On top of the CLI's pattern, layer:

1. **The relevant rules**: cite specific `.agent-os/rules/*.md` files the work must follow.
2. **Past decisions**: link to memories or ADRs that constrain the choice.
3. **Naming conventions**: explicitly state any (e.g. "props interfaces are `{ComponentName}Props`").
4. **Test plan**: mention what tests the work must add (linked to TDD skill).
5. **Verification gate**: state which verification layers apply.

## Step 3 — Use this template

```
<context>
<!-- Project state, relevant files, existing patterns -->
</context>

<task>
<!-- Specific action with acceptance criteria -->
</task>

<rules-to-apply>
<!-- e.g. .agent-os/rules/testing.md §mocking, .agent-os/rules/typescript.md §types -->
</rules-to-apply>

<past-decisions>
<!-- e.g. ADR-007 chose Zustand over Redux; [[concepts/zustand-pattern]] -->
</past-decisions>

<constraints>
<!-- "don't change the public API"; "must pass mutation-test gate"; etc. -->
</constraints>

<verification>
<!-- which 7-layer verification layers apply; what PASS looks like -->
</verification>

<report-back>
<!-- what summary you want from the sub-agent (file paths, line counts, follow-ups) -->
</report-back>
```

Note: the XML tag style is Claude's preference. For Codex, translate to numbered
sections. For Pi, use Pi-native sections. The per-CLI refiner skill does this.

## Step 4 — Sanity-check before sending
- Read the refined prompt once. Can a fresh agent execute without asking back?
- If yes, send. If no, add the missing context.

# Output shape
The refined prompt itself, ready to paste into the target CLI's spawn command.

# Anti-patterns (refuse)
- Sending a raw user request to a sub-agent without team-context layering.
- Layering so much context the prompt is longer than the work.
- Forgetting to specify the verification gate.
