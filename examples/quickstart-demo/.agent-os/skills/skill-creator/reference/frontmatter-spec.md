# Frontmatter Spec

Canonical YAML frontmatter schema for `SKILL.md`. Every skill MUST have this header. No exceptions.

## Schema

```yaml
---
name: <kebab-case-slug>          # REQUIRED. Matches directory name. Lowercase, hyphens only.
description: <one-paragraph>     # REQUIRED. The relevance-score input. See rules below.
version: <semver>                # OPTIONAL. Default: 1.0.0
compat: <runtime list>           # OPTIONAL. e.g. "claude-code, codex, pi"
deprecated: <date|null>          # OPTIONAL. Set to date if skill is being retired.
supersedes: <slug>               # OPTIONAL. Name of skill this replaces.
---
```

## Field rules

### name (required)

- Kebab-case slug (lowercase, hyphens, no spaces, no underscores).
- Matches the directory name exactly: `skills/<name>/SKILL.md`.
- Globally unique across the skills library.
- Stable: once shipped, never rename. If you must, set `supersedes` on the new skill and `deprecated` on the old.

### description (required, load-bearing)

This is the single most important field. The agent picks skills using semantic similarity to this string. Bad description = invisible skill.

**Required structure** (in order):

1. **Verb start.** Begin with the action: "Author...", "Write...", "Diagnose...", "Validate...".
2. **Trigger list.** Enumerate 2–4 specific triggers using "when X" or "when user does Y".
3. **Capability tag.** Close with 1 sentence summarising the output.

**Length:** 30–80 words. Anything shorter is unmatched on many task phrasings; anything longer dilutes the signal.

**Bad examples (do not ship):**

- "A skill for testing." (no triggers, no capability)
- "Helps the agent write better code." (no specifics, will never match)
- "This skill is used when you want to test things and possibly also lint and maybe format." (multiple concerns, hedging language)

**Good examples:**

- "Write Vitest unit tests using AAA structure and 'should X when Y' naming when the user mentions tests, coverage, or red-green workflow. Produces test files plus a coverage delta summary."
- "Diagnose hard bugs with hypothesis-first methodology when user reports breakage, regression, or unexpected behaviour. Outputs a ranked hypothesis list plus a reproducer."

### version (optional)

Semver. Bump on breaking changes (renamed steps, removed sections). The framework treats `1.x` as the stable contract; agents do not break on minor bumps.

### compat (optional)

Comma-separated runtimes the skill targets. Default: all. Use this when a skill depends on a runtime-specific tool (e.g. `compat: claude-code` for a skill that calls Claude-Code-only MCP servers).

### deprecated / supersedes

When retiring a skill, set both fields. The `skill-discovery` skill treats `deprecated` skills as invisible and routes matches to the `supersedes` target.

## Validation

A skill ships only if frontmatter:

- [ ] Has `name` matching directory.
- [ ] Has `description` starting with a verb, listing 2–4 triggers, ending with the capability.
- [ ] Description is 30–80 words.
- [ ] If `supersedes` is set, the referenced skill exists.

Lint with:

```bash
head -10 SKILL.md  # eyeball the block; CI parser pending
```

## Why this matters

The agent does NOT read every `SKILL.md` body on every task. It reads the descriptions, scores relevance, and only opens the matched skill(s). The description is the gatekeeper. Treat every word as expensive.
