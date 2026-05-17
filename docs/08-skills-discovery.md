# Skills Discovery (Cornerstone Meta-Doc)

> Applies to: Claude Code, Codex, Pi. The mandatory pre-task scan that prevents the agent from reinventing capabilities it already has. Inspired by Matt Pocock's pattern of "skill-discovery first, action second".

## Why skills must be discovered, not guessed

An agent that doesn't check `skills/` before acting will:

- Reimplement a procedure that already exists (token waste, drift).
- Skip the project's anti-gaming primitives the skill was wrapping.
- Apply an outdated convention because its training data has the old way.
- Miss the verification chain because the skill encodes the operator's preferences.

The Framework treats skill discovery as a **gate**: the agent does not proceed on a non-trivial task without scanning `skills/` first. The scan is cheap (a directory listing + the `description:` line of each `SKILL.md`); the cost of skipping it is high.

## The decision tree

```
User message
   │
   ▼
[Scan skills/ — read each SKILL.md frontmatter `description:` line]
   │
   ▼
Does any skill apply to this message?
   ├─ YES → Invoke the skill. Announce: "Using <skill> to <purpose>."
   │
   └─ NO  → Can skill-creator make one?
              ├─ YES (recurring task, will see again)
              │     → Invoke skill-creator. Author SKILL.md. Then use it.
              │
              └─ NO (one-off; not generalizable)
                    → Proceed without a skill. Note in session log
                      why no skill applied.
```

The tree is enforced by `skills/skill-discovery/SKILL.md`, which is itself the cornerstone skill. Every other skill assumes skill-discovery ran before it.

## Red-flag rationalizations (and reality checks)

The agent will be tempted to skip the scan with rationalizations like these. Each has a one-line reality check.

| Rationalization | Reality check |
|-----------------|---------------|
| "This is too small for a skill." | Then skill-discovery completes in a few hundred tokens. Cost is negligible; cost of missing is high. |
| "I know how to do this." | Your training data doesn't know the project's conventions. The skill does. |
| "There can't be a skill for this specific thing." | Read the descriptions; the scan tells you in seconds. |
| "I'll scan after I draft." | Drafting without a skill that exists is the waste you're trying to avoid. |
| "Skills are just templates; I can do better." | Skills are codified team agreements. "Doing better" without team buy-in is drift. |

## How agents announce skill invocation

When the agent invokes a skill, it announces in one line, before running the skill body:

```
Using llm-wiki to ingest the new source.
Using context-compression to summarize the session before continuing.
Using post-edit-hook to enforce the testing/pytest.md rule.
```

This makes the agent's behavior auditable in transcript. A reader scrolling the chat can see which skills fired and why. It also acts as a verification anchor — a transcript that claims `PASS` but never announces the verification skill is suspect.

## Per-CLI skill-loading mechanism

The three CLIs load skills differently. Same conceptual model: a named instruction set, frontmatter + body, invoked by name.

### Claude Code

Skills live at:

- `.claude/skills/<name>/SKILL.md` — project-scoped
- `~/.claude/skills/<name>/SKILL.md` — user-scoped

Claude loads them automatically and invokes via the `Skill` tool. The session reminder lists available skills with their descriptions. To invoke, the agent calls `Skill({ skill: "<name>" })`. The harness can also force-load via slash commands `/<name>`.

### Codex

Codex doesn't have a built-in skills directory. Skills are surfaced through `AGENTS.md`:

```markdown
# AGENTS.md

## Available skills

- `skills/llm-wiki/` — ingest sources, query the wiki, lint links
- `skills/context-compression/` — anchored summary at end of long sessions
- `skills/skill-discovery/` — MANDATORY pre-task scan
- ...

To invoke, read the body of the matching SKILL.md and follow its steps.
```

Codex reads `AGENTS.md` on session start and treats the skill list as part of its context. Invocation is implicit (Codex reads `SKILL.md` body before acting) and announced inline ("Using llm-wiki to …").

### Pi

Skills install as capability packages, on demand:

```bash
pi install @framework/skill-discovery
pi install @framework/llm-wiki
pi install @framework/context-compression
```

Each package writes a `SKILL.md` into `~/.pi/capabilities/<skill>/` and registers any tools it exposes over Pi's JSON-RPC stream. Pi's `SYSTEM.md` references the capability index. To invoke, the agent calls the registered tool (or reads `SKILL.md` and follows steps for skills without tool exposure).

Pi-specific consequence: skills consume context only when installed. Uninstalling a skill frees its budget. This is leverage for tight-context sessions.

## Index discoverability

Regardless of CLI, the agent must be able to discover the skill list cheaply. The Framework's contract:

- `skills/INDEX.md` at repo root lists every skill with a one-line description.
- `AGENTS.md` references `skills/INDEX.md`.
- The skill-discovery skill reads `skills/INDEX.md` first; if missing or stale, it falls back to scanning each `SKILL.md`.

A stale index is worse than no index — wire the post-edit hook on `skills/**/SKILL.md` to regenerate `skills/INDEX.md`. See `skills/post-edit-hook/SKILL.md`.

## Cross-reference

- `skills/skill-discovery/SKILL.md` — the runnable scan procedure
- `skills/skill-creator/SKILL.md` — author a new skill when none applies
- [Setup checklist](./01-setup-checklist.md) L4 — skill-discovery is installed before any other automation
- Matt Pocock's *skill-discovery* pattern — the inspiration
