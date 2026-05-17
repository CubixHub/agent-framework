---
name: skill-discovery
description: Match every incoming task against the available skills library and invoke any applicable skill BEFORE any other tool call. Run at the start of every turn that involves doing something. If no skill matches above 30% confidence, invoke skill-creator. Skills must be discovered, never guessed.
---

# When to use

**Invoke this skill at the start of every task.** Not optional. Not conditional. The first thing the agent does on any non-trivial request is run skill-discovery.

Specifically:

- User asks the agent to do anything (build, debug, write, refactor, plan, deploy).
- User asks a question that may have an associated skill (e.g. "how do I test X?" → invoke the testing skill).
- The agent is about to call any tool other than `Read` to inform itself about a file the user mentioned.

Skip only when:

- The agent is in a continuing turn of an already-invoked skill (don't re-discover mid-skill).
- The user message is purely informational ("thanks", "ok") with no action implied.

# How to execute

The four-step protocol. Do not deviate.

## Step 1 — List available skills

```bash
find /home/boldog/Desktop/Framework/skills -maxdepth 3 -name "SKILL.md" | head -50
```

For each `SKILL.md`, read **only the frontmatter** (lines 1–10). The `description` field is the relevance-score input. Do NOT read the body yet — that is wasteful.

## Step 2 — Match the task against skill descriptions

For each skill description, ask: "Does this skill's stated trigger match what the user is asking?"

Score each candidate:

- **Strong (≥70%)**: explicit trigger word appears, deliverable matches request.
- **Plausible (30–69%)**: thematic overlap, one trigger keyword, deliverable close to request.
- **Weak (<30%)**: tangential. Ignore.

Multiple strong matches are common. Prefer the most specific. (A "test-driven-development" skill beats a generic "engineering" skill for a TDD request.)

## Step 3 — Decide

```
If at least one strong (≥70%) match:
   → Invoke the best-matching skill. Announce it explicitly: "Using <skill> to ..."
If only plausible (30–69%) matches:
   → Invoke the best one. State the reason: "Best fit is <skill> because ..."
If only weak (<30%) matches:
   → Invoke skill-creator. The task represents a missing capability.
```

See `reference/discovery-flowchart.md` for the visual diagram.

## Step 4 — Announce and invoke

Before any other tool call, the agent emits a single line:

> "Using <skill-name> to <one-line summary of what this skill will do for this task>."

This is non-negotiable. Silent skill invocation is forbidden — it makes the agent's reasoning auditable and prevents the rationalisation pattern of "I'll just do this directly, no need for the skill."

Then read the body of `SKILL.md` for that skill and follow its procedure.

# Quality bar

- [ ] Skill discovery ran at the start of the turn (every turn that involves action).
- [ ] Every skill's frontmatter `description` was read before scoring.
- [ ] The chosen skill (or `skill-creator`) was announced explicitly.
- [ ] If no skill matched ≥30%, `skill-creator` was invoked rather than free-handed work.
- [ ] The agent did NOT call any other tool before announcing the chosen skill.

# Anti-patterns

These are the rationalisation patterns the agent will reach for to avoid the protocol. Refuse each:

- **"This is just a simple question."** Even simple questions can have skills. Run the match anyway. The protocol is cheap; skipping it is expensive.
- **"I need more context first, let me Read some files."** No. Skill discovery happens BEFORE reading files. Many skills explicitly say "do not read the codebase first" — by reading, you have already broken that skill.
- **"I'll do this directly and it'll be faster."** This is the failure mode the protocol exists to prevent. Direct execution is what produces brittle, inconsistent agent work. Use the skill or create the skill. There is no third option.
- **"None of the skills look quite right, I'll just wing it."** Two unrelated skills are still better than ad-hoc. If you find yourself winging it, invoke `skill-creator` and capture the pattern.
- **"The user didn't say `use a skill`."** Irrelevant. The user gave you a task. The protocol decides on skills, not the user.

See `reference/red-flags.md` for the extended catalogue of rationalisation patterns and how to recognise them.

# The non-negotiable

Skills are discovered, not guessed. Every framework agent runs this protocol. The output of the protocol is one of: a skill invocation, or a `skill-creator` invocation. There is no third branch.

If you find yourself executing user work without having run skill-discovery, stop. Back up. Run the protocol. Re-enter with the right skill.

# Reference

- `reference/discovery-flowchart.md` — visual decision tree
- `reference/red-flags.md` — rationalisation patterns and reality checks
