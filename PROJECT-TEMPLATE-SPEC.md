# Project Template Spec — Agent-Buildable Software Project

> A spec for setting up a new software project so that a coding agent (Claude Code, Factory Droid, Cursor, Codex, or equivalent) can plan it deeply, document it consistently, decompose it cleanly, and verify its own work as a real user would. Hand this entire doc to a fresh agent and a fresh repo; it has everything needed to reproduce the pattern.

## What this spec produces

When an agent follows this spec end-to-end, the resulting repo has:

1. **A living wiki** the agent maintains as it learns (Karpathy's LLM-wiki pattern: sources → entities/concepts → questions/answers; never re-derived from raw on every query).
2. **A numbered idea backlog** with effort × impact ratings and per-ID detail blocks.
3. **A package-based architecture decomposition** into 15–30 small packages across 4–6 dependency layers, each with its own README + ADR folder.
4. **Project- and package-level Architecture Decision Records** with explicit numbering, accepted-status frontmatter, and consequence tracking.
5. **A master plan** (`PLAN.md` + `packages/README` + `packages/ARCHITECTURE` + `packages/INTEGRATION` + `packages/PHASES` + `STATUS`) that an outsider can read in 30 minutes and understand the whole project.
6. **Agent-runtime configuration** (`AGENTS.md` + `CLAUDE.md` + `.factory/rules/` + `.factory/skills/` + `.factory/hooks/`) so the agent applies the same conventions on every edit.
7. **A verification-first principle** baked into the architecture so no work is "done" until it's been verified as a real user would experience it.
8. **A phased build plan** with explicit pre-Week-1 spike experiments that de-risk before implementation begins.

## How to use this spec

This doc is hierarchical. Each section explains a layer of the structure. Sections build on each other — read top to bottom. The final section is a **Setup Checklist** with concrete commands.

The spec assumes the agent can:
- Read/write files in a working directory
- Run bash commands
- Spawn parallel sub-agents (for dispatch patterns)
- Commit to a git repo

It does not assume any specific framework, language, runtime, or vendor.

## Glossary

| Term | Meaning |
|---|---|
| **Wiki** | The `wiki/` directory containing the agent's accumulated knowledge |
| **Idea** | A numbered backlog entry (`<PREFIX>-NNN`) representing a buildable thing |
| **Package** | A single-concern subfolder under `packages/` (or `wiki/plan/packages/`) |
| **ADR** | Architecture Decision Record — a frontmatter'd markdown doc capturing one design decision |
| **Layer** | Dependency depth (L0 foundations, L1 coordination, etc.) |
| **Phase** | Time-based delivery milestone (P0 spikes, P1 MVP, P2..P5 progression) |
| **Hook** | A script the agent runtime fires on a specific event (post-edit, pre-commit, etc.) |
| **Skill** | A reusable instruction set the agent invokes by name |
| **Spike** | A time-boxed experiment that de-risks an unknown before implementation |
| **Persona** | A configured "user profile" used to drive verification (novice / expert / etc.) |

---

## 1. Repository skeleton

The full file tree the agent creates. **Every directory below should exist after day-1 setup, even if some are empty placeholders.**

```
<repo-root>/
├── README.md                     One-paragraph project pitch + pointer to PLAN.md
├── AGENTS.md                     Canonical agent-runtime entry doc (read by every agent)
├── CLAUDE.md                     Claude-Code-specific overlay; usually points to AGENTS.md
├── GEMINI.md                     (optional) Gemini CLI overlay
├── .gitignore                    Standard; must include .env*, secrets, build artifacts
├── .factory/
│   ├── settings.json             Hook + skill wiring for Factory Droid
│   ├── memories.md               Append-only project-decision log
│   ├── rules/
│   │   ├── general.md            Universal rules (commit style, never push without ask, etc.)
│   │   ├── <lang-1>.md           Per-language rules (e.g., typescript.md, rust.md)
│   │   ├── api.md                API-design rules (if applicable)
│   │   ├── testing.md            Testing rules
│   │   └── security.md           Security rules (lethal-trifecta, secret-handling)
│   ├── skills/
│   │   └── <skill-name>/
│   │       ├── SKILL.md          Skill definition
│   │       └── reference/        Source material referenced by the skill
│   └── hooks/
│       ├── post-edit.sh          Dispatcher invoked on Create/Edit/ApplyPatch
│       ├── format-on-edit.sh     Language-aware formatter
│       ├── wiki-lint.sh          Wikilink validator (informational, never blocks)
│       └── memory-capture.py     Optional: auto-capture significant decisions
│
├── wiki/                         The agent's living knowledge base
│   ├── SCHEMA.md                 Wiki page conventions (read this before any wiki edit)
│   ├── README.md                 (optional) what the wiki is
│   ├── index.md                  The catalog of every page (agent maintains)
│   ├── log.md                    Append-only audit log of wiki operations
│   ├── PLAN.md                   The master project plan
│   ├── IDEAS.md                  Numbered backlog (the idea board)
│   ├── STATUS.md                 Current-state snapshot + blocker map
│   ├── raw/                      Immutable source layer (PDFs, screenshots, transcripts)
│   ├── sources/                  Cards for ingested sources
│   ├── entities/                 Cards for orgs / products / people / tools
│   ├── concepts/                 Cards for ideas / patterns / techniques
│   ├── questions/                Cards for resolved Q&A
│   ├── IDEAS-details/            Per-ID detail blocks (one file per batch)
│   ├── plan/                     Project planning detail
│   │   ├── verification-strategy.md
│   │   ├── security.md
│   │   ├── reuse-map.md          Build-vs-adopt-vs-extend decisions per external dep
│   │   ├── adr/                  Project-level ADRs (cross-cutting)
│   │   └── packages/             Per-package decomposition (see §5)
│   │       ├── README.md         Master overview of all packages
│   │       ├── ARCHITECTURE.md   Layer model + dependency graph
│   │       ├── INTEGRATION.md    How packages talk (hooks/schemas/manifest)
│   │       ├── PHASES.md         Package-by-package phase ramp
│   │       └── <package-name>/
│   │           ├── README.md
│   │           ├── adr/
│   │           └── impl/         (optional) implementation-readiness docs
│   └── spikes/                   Findings from P0 spike experiments
│
├── packages/                     Actual code (created at implementation time)
└── tests/                        Cross-package integration tests
```

The `packages/` (code) and `wiki/plan/packages/` (docs) folders mirror each other — every code package has a corresponding wiki entry; every wiki package will eventually have code.

---

## 2. The wiki layer (Karpathy LLM-Wiki pattern)

**Mental model**: instead of re-deriving knowledge from raw sources on every query (classic RAG), the agent maintains a persistent, compounding markdown knowledge base. The wiki is the agent's long-term memory.

### Page categories

| Folder | What lives here | Mutability |
|---|---|---|
| `wiki/raw/` | Immutable source files (PDFs, transcripts, screenshots, dumps) | **Never modify** |
| `wiki/sources/` | One card per ingested source — what it is, why it matters, key claims | Agent writes |
| `wiki/entities/` | One card per org / product / person / tool — what they do, who they are | Agent writes |
| `wiki/concepts/` | One card per idea / pattern / technique — what it is, how it works | Agent writes |
| `wiki/questions/` | One card per non-trivial answered question — what was asked, what was concluded | Agent writes |

### Required frontmatter (every wiki page)

```yaml
---
title: <short human title>
type: source | entity | concept | question
tags: [list, of, kebab-case, tags]
updated: YYYY-MM-DD
sources: [optional list of wikilinks to source pages]
---
```

### Filename convention

- All lowercase
- Words separated by hyphens (kebab-case)
- `.md` extension
- Slug should match the wikilink reference

### Cross-references — wikilinks

The agent uses Obsidian-style wikilinks: `[[category/slug]]` or `[[category/slug|display text]]`.

- **Link liberally.** A link to a page that doesn't yet exist is a TODO marker, not an error.
- **Cite every non-trivial claim.** Every fact links to the source page that supports it.
- **Use `.md` suffix sparingly.** Wikilinks without `.md` are preferred — many lint tools treat `[[foo.md]]` and `[[foo]]` as different targets.

### Surface contradictions, don't paper over them

When the agent encounters conflicting evidence, it creates a callout:

```markdown
> ⚠ Contradicts [[other-page]] as of YYYY-MM-DD — <one-sentence reason>
```

Never silently resolve contradictions; explicit divergence is signal.

### `wiki/SCHEMA.md` is canonical

`wiki/SCHEMA.md` documents every above convention with examples. The agent reads it before any wiki operation. When conventions evolve, update `SCHEMA.md`; don't propagate the change ad-hoc.

### `wiki/index.md` is the catalog

A flat catalog of every page by category. The agent maintains this on every wiki write. It's the human's entry point to the wiki.

### `wiki/log.md` is the audit trail

Append-only chronological log of wiki operations. Every batch of wiki edits ends with a log entry summarising what changed and why.

### Operations the agent supports on the wiki

| Trigger phrase | Workflow |
|---|---|
| "ingest this", "wiki this", URL/file handed over | **Ingest** → create source card + linked concept/entity cards |
| "what does the wiki say about X?", "what did we decide about Y?" | **Query** → read `index.md`, drill in, file the answer back as a `questions/` page if it touched ≥ 2 wiki pages |
| "lint the wiki", "audit the wiki" | **Lint** → scan for broken wikilinks, orphans, missing concept pages, stale pages |
| _End of any session with meaningful new knowledge_ | **Unprompted file-back** — don't let knowledge vanish into chat history |

---

## 3. The idea board

A **single source of truth** for "things to build, steal, research". Lives at `wiki/IDEAS.md`. Detail blocks live at `wiki/IDEAS-details/`.

### Format

Every idea has:
- **ID** — `<PREFIX>-NNN`, sequential, **never reused**. Pick a 2–3 letter prefix at project start (e.g., the project initials).
- **Status** — emoji marker: 📋 proposed · 🔨 in-progress · ✅ done · 🛑 deferred · 🗑️ rejected
- **Source** — wikilinks to the wiki pages that inspired it
- **Title** — 1-line description
- **Effort** — T-shirt size: XS / S / M / L / XL
- **Impact** — H / M / L

When status changes, append a one-line dated note rather than rewriting history.

### IDEAS.md structure

```markdown
---
title: <Project> Idea Board
type: ideas
updated: YYYY-MM-DD
---

# <Project> Idea Board

## Format
<one-paragraph format explanation>

## Index (status snapshot)
Total ideas: **N**

### From the <topic-or-source> batch (<PREFIX>-NNN..NNN) — N ideas

| ID | Status | Title | Effort | Impact |
|---|---|---|---|---|
| <PREFIX>-001 | 📋 | <title> | M | H |
| ... |
```

### Detail blocks — `wiki/IDEAS-details/<batch-name>.md`

When an idea graduates from a table row to something the agent must reason about, it gets a detail block. **Authored on demand**, not eagerly. Detail blocks live in batch files (one file per related cluster) rather than per-ID files (avoid 100s of tiny files).

Each detail block:

```markdown
## <PREFIX>-NNN — <title>
**Effort:** <size> · **Impact:** <H|M|L> · **Phase:** <P0|...|P5> · **Owner module/package:** <pkg>

### Problem
<2-4 sentences: what failure mode this addresses>

### Approach
<3-6 sentences: concrete technique, source, deviations>

### Dependencies
- <list of upstream IDs/packages>

### Acceptance criteria
- <observable check #1>
- <observable check #2>

### Risk
<1-2 sentences: what could go wrong + mitigation>

### Related
[[<PREFIX>-XXX]] · [[plan/packages/<pkg>/README]]
```

### Numbering policy

- **Sequential within a batch**, with gaps allowed between batches.
- **Never reuse a number** even if the idea is rejected — keep the audit trail.
- **Document gaps** in `IDEAS.md` (e.g., "<PREFIX>-029..<PREFIX>-099 reserved for future foundational batches").
- When a new batch fills a gap, mark them clearly as "proposed for review" — they need human ratification of Effort × Impact.

---

## 4. Agent-runtime configuration

The agent's behavior is configured through 5 surfaces. The agent reads these on every session start.

### `AGENTS.md` (canonical)

The single entry-point doc every agent runtime reads. Sections:

```markdown
# <Project> — Agent Guide

## Project
- Repo location, remote, owner, default branch, status

## Where things live
- Pointers to AGENTS.md, rules, skills, hooks, wiki, memory

## Conventions
- Commit-message tone (imperative, short subject)
- Git push policy (never auto-push; ask first)
- Confidentiality (treat private repo content as such)

## Stack
- Languages, frameworks, runtimes (TBD if unchosen)

## Slot table
- build / test / lint / typecheck / format commands per language
```

### `CLAUDE.md` (Claude Code overlay)

Re-states the agent's project context for Claude Code specifically. Usually points to `AGENTS.md` as the source of truth.

### `.factory/rules/*.md` (coding standards)

One file per rule category. Common files:
- `general.md` — universal rules (commits, security defaults, push policy)
- `<language>.md` — per-language style
- `api.md` — API design rules (auth, versioning, errors)
- `testing.md` — testing rules (no mocks where mocks burned us, integration coverage targets)
- `security.md` — security rules (lethal-trifecta avoidance, secret-handling)

Each rule file is short (1 screen). The agent applies them when editing matching files.

### `.factory/skills/<skill-name>/SKILL.md`

A skill is a reusable instruction set the agent invokes by name. Skills have:

```markdown
---
name: <kebab-case-skill-name>
description: <one-line summary used for relevance scoring>
---

# When to use this skill
<situations that trigger this skill>

# How to execute
<concrete steps>

# Reference
<links to reference/ subfolder with source material>
```

Example skills the spec includes by default:
- `llm-wiki` — the wiki ingest/query/lint operations
- (project-specific skills added as needed)

### `.factory/hooks/*.sh`

Scripts the agent runtime fires on events. Required hooks:

**`.factory/hooks/post-edit.sh`** — dispatcher invoked on every Create/Edit/ApplyPatch:
```bash
#!/usr/bin/env bash
# Reads JSON tool_input from stdin: {"tool_input": {"file_path": "/abs/path"}}
input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path')
case "$file_path" in
  *.md)
    bash "$(dirname "$0")/wiki-lint.sh" <<<"$input"
    ;;
  *.ts|*.tsx|*.js|*.jsx)
    bash "$(dirname "$0")/format-on-edit.sh" <<<"$input"
    ;;
  # ... per-language dispatch
esac
```

**`.factory/hooks/wiki-lint.sh`** — scans for broken wikilinks; outputs a `systemMessage` if any found. **Informational, never blocks.** The agent treats output as a punch-list.

**`.factory/hooks/format-on-edit.sh`** — runs the language-appropriate formatter (prettier, rustfmt, etc.) and writes back.

Hooks expect `$DROID_PROJECT_DIR` (or equivalent project-root env var) to be set by the runtime.

### `.factory/settings.json`

The wiring file: which hooks fire on which events, which skills are auto-loaded, etc. Format depends on the runtime (Factory Droid, Claude Code, etc.).

### `.factory/memories.md`

Append-only project-decision log. The agent writes a dated bullet here when a non-obvious decision is made. Distinct from the wiki: memories are compact decisions; the wiki is accumulated research.

---

## 5. Project planning structure

Three planning surfaces, each owning a different time horizon.

### `wiki/PLAN.md` — the master plan (slow-changing)

The "what is this project trying to be" doc. Sections:

```markdown
# <Project> — Game Plan

## Vision
<1-paragraph: what the project does, why it matters, target user>

## The N long-running failure modes — and which ideas address each
| # | Failure mode | Primary ideas that address it |
<table of named failure modes ↔ idea IDs>

## Architecture — N packages, M layers
<package-by-layer table; mirrors packages/README.md>

## The 5-phase build plan
| Phase | Goal | Packages built/adopted | Duration | "Done" criterion |
<P1..P5 table>

## Top N risks
<numbered risk register with mitigations>

## What "done" looks like per phase — measurable criteria
<P1..P5 checklists>

## Open questions (need to resolve before P1)
<numbered, must-decide-before-implementation list>

## Idea-board cross-reference
<pointer to IDEAS.md>
```

**Updated quarterly or on major architectural change. Not edit-on-every-task.**

### `wiki/STATUS.md` — current state + blocker map (fast-changing)

The "where are we today, what's blocked on what" doc. Sections:

```markdown
# Where We Are — and What's Blocked on What

## Current state — at a glance
<table: docs / ADRs / IDs / packages / lines-of-code>

## What ships in P<current> — packages
<list of packages active this phase>

## Pre-P<current> human-sign-off requirements
<decisions that need human approval before implementation>

## Pre-P<current> implementation-blocking ADR gaps
<ADRs that must be authored before affected package implementation>

## Architectural blast-radius hotspots
<decisions whose reversal cascades across multiple packages>

## Cross-package coupling worth tracking explicitly
<dependencies that span layers; architectural debt by design>

## P<current>-elevation candidates — actionable right now
<IDs that are XS/S effort, zero blocking deps>

## Open documentation backlog (not blocking)

## What's intentionally out of scope (right now)

## What "done" looks like per phase

## The one-sentence current-state summary
> <one sentence>
```

**Updated after every meaningful work session.** This is the human's daily entry point.

### `wiki/plan/` — sub-plans (medium-changing)

Cross-cutting planning docs that don't fit cleanly into a single package:

- `verification-strategy.md` — how the project verifies its own work (see §9)
- `security.md` — threat model index (defended threats / explicitly-not-defended threats)
- `reuse-map.md` — adopt-vs-build decisions per external dependency
- `spikes/<spike-name>.md` — findings from each pre-Week-1 spike (see §10)

### Hierarchy and update frequency

```
PLAN.md              quarterly / on architectural change
STATUS.md            every work session
plan/*.md            on cross-cutting decision
packages/*/README    on package architectural change
packages/*/adr/      on package design decision
```

---

## 6. Package architecture

The project decomposes into 15–30 small packages organized in 4–6 dependency layers. Each package owns exactly one concern. Composition over inheritance. **When a failure happens in production, it must have an owner package.**

### Why microservices over a monolith

1. **The agent extension contract IS the boundary.** Most modern agent runtimes already expose a package-registration mechanism (Pi `pi:` key, Claude Code skills, etc.) — this is your RPC layer. Don't invent another.
2. **Failure modes get owners.** Each long-running failure mode (context exhaustion, crash recovery, drift, cost runaway) gets its own owner-package. When a failure happens, it has an owner.
3. **Adoption is cheap.** External packages can be wrapped one at a time without affecting the rest. Build vs adopt is a per-package decision.

### Layer model

Pick a depth that fits your project (typically 4–6 layers). Generic template:

| Layer | Purpose | Dep rule |
|---|---|---|
| **L0 — Foundations** | State primitives: process, sandbox, storage, routing, trace, file-view | No internal deps |
| **L1 — Coordination** | Permissions, compaction, planning, cost, verification | Depends on L0 only |
| **L2 — Delegation & memory** | Subagents, recursive workers, knowledge objects, behavioural fingerprints | Depends on L0–L1 |
| **L3 — Mission orchestration** | Multi-day state machine, checkpointing, evals, A/B | Depends on L0–L2 |
| **L4 — Verification** | Evaluator, judges, anti-gaming, sandbox tiers | Sits orthogonally; reads L0–L3 but writes verdicts |
| **L5 — Embedded SDKs** | Build-time deps consumed by the project's built apps | Consumed by targets, not by the harness |

### Package folder structure

```
wiki/plan/packages/<package-name>/
├── README.md                Package overview
├── ARCHITECTURE.md          (optional) internal module layout if > 3 modules
├── adr/
│   ├── adr-NNN-<slug>.md
│   └── ...
└── impl/                    (optional) implementation-readiness companion docs
```

### Master docs in `wiki/plan/packages/`

Four files at the root of `packages/` that explain the whole decomposition:

1. **`README.md`** — master overview, elevator pitch, the N packages by layer, failure-mode ownership map
2. **`ARCHITECTURE.md`** — layer model + full dependency graph + cross-cutting infrastructure
3. **`INTEGRATION.md`** — extension protocol, shared schemas, hook ordering, manifest contract
4. **`PHASES.md`** — package-by-package phase ramp (P0 spikes → P5)

### Per-package README template

Every package README has the same 11 sections:

```markdown
---
title: <package> — <one-line tagline>
type: package
tags: [package, <layer>, <key topics>]
updated: YYYY-MM-DD
status: planned
---

# <package>

> <one-sentence elevator pitch>

## Owner-concern
<2-4 sentences: which failure mode this package owns and why it's a separate package>

## What it does
<3-5 paragraphs: responsibilities, key design decisions, what it does NOT do>

## Public API
### Hooks registered
### Tools exposed
### Schemas emitted
### Schemas consumed

## Internal architecture
<modules, key data structures, main control flow>

## Adoption strategy
<build / adopt as-is / adopt+extend, with rationale>

## Dependencies
<internal package deps + external NPM/cargo/PyPI/etc deps>

## Phase ramp
<when first ships; what's in P1 vs later>

## Configuration
<manifest block this package reads; show YAML>

## Open ADRs
<2-4 architectural decisions still to make>

## Related ideas
<2-6 idea IDs from IDEAS.md that map to this package>

## Related
<cross-links to packages/README, ARCHITECTURE, sibling packages>
```

### Cross-cutting infrastructure (shared, not packaged)

Some concerns sit outside the package boundary but are used by every package:

- **Shared schema set** — 8–12 versioned schemas that every package speaks (e.g., `EventEnvelope`, `CostEvent`, `ArtifactMutation`). Lives in a dedicated `*-schemas` package, treated as infrastructure.
- **Manifest contract** — single YAML file at repo root declaring which packages are active + per-package config.
- **Extension protocol** — hooks + tools + slash commands wired through the agent runtime's extension API.
- **Hook ordering** — canonical sequences per event, declared in a project-level ADR.

---

## 7. ADR conventions

Every non-trivial architectural decision becomes an ADR. ADRs are the unit of "we thought about this and chose X for reason Y".

### Two ADR namespaces

| Folder | Numbering | What lives there |
|---|---|---|
| `wiki/plan/adr/` | adr-001..099 (project-level, low numbers) | Cross-cutting decisions affecting ≥ 2 packages |
| `wiki/plan/packages/<pkg>/adr/` | adr-NNN (package-level, project-scoped numbering) | Decisions affecting one package |

A cross-cutting ADR may use higher numbers (e.g., adr-101+) if a particular package's ADR namespace started there for sequencing reasons. Document the convention in a project-level meta-ADR if non-obvious.

### ADR template

```markdown
---
title: 'ADR-NNN: <decision in one sentence>'
type: adr
tags: [<package-name>, <topic-tags>]
updated: YYYY-MM-DD
status: accepted | superseded | proposed | rejected
---

# ADR-NNN — <short slug>

## Context
<2-4 paragraphs: what the situation is, why a decision is needed,
the alternatives considered. Name options A / B / C.>

## Decision
<2-3 sentences: the choice, in plain language>

## Rationale
1. <numbered reasons; one paragraph each>
2. ...

## Consequences
- **In**: <positive consequences>
- **Out**: <costs / things this ADR accepts as the price>
- **Coupling**: <dependencies on other packages>
- **Required**: <follow-on work this ADR creates>

## Implementation
<optional: concrete sketch — types, function signatures, schema snippets>

## Test cases
<optional: numbered observable checks that prove the decision works>

## Related
<wikilinks to README, sibling ADRs, ideas, sources>
```

### When to write an ADR

- A new design decision that affects how a package is built
- A package boundary change
- A schema or contract change
- A change in conventions used across the project

### When NOT to write an ADR

- Bug fixes (use commit messages)
- Implementation details that don't affect the public interface
- Decisions reversed within the same session

### ADR status lifecycle

```
proposed → accepted → (later) superseded by ADR-XXX
                   ↓
                rejected
```

Never delete an ADR. If superseded, set `status: superseded` and add a `> Superseded by [[adr-NNN-...]]` callout at the top.

### Decisions needing human sign-off

When an ADR encodes a decision the agent cannot make alone (security policy, data-loss behaviour, onboarding-vs-production tradeoff), the ADR ends with:

```markdown
- **Human sign-off needed**: <one-sentence question> Decide before <gate>.
```

`STATUS.md` tracks these explicitly. When resolved, the ADR is updated:

```markdown
- **Resolved YYYY-MM-DD (user sign-off)**: <decision>. <one-sentence rationale>.
```

---

## 8. Hooks and lints

The agent runtime fires hooks on events. These automate the "small things" that would otherwise drift.

### Required hooks

#### `post-edit.sh` — dispatcher

Fires on Create/Edit/ApplyPatch. Reads `{"tool_input": {"file_path": "..."}}` from stdin. Dispatches by file extension:

- `.md` files in `wiki/` → invoke `wiki-lint.sh`
- Source files (`.ts`, `.rs`, `.py`, etc.) → invoke `format-on-edit.sh`
- Config files (`.yaml`, `.toml`, `.json`) → schema-validate if a schema is registered

The dispatcher writes to stdout (`systemMessage` JSON for the runtime to surface to the agent) but never blocks the edit.

#### `wiki-lint.sh` — broken-wikilink scanner

For every `[[wikilink]]` in the edited file, check that the target file exists. Report broken links with their target. **Informational only — never blocks.** Treat broken links as a punch-list the agent works through.

Recommended implementation:
```bash
#!/usr/bin/env bash
input=$(cat)
file=$(echo "$input" | jq -r '.tool_input.file_path')
[[ "$file" != *.md ]] && exit 0
[[ "$file" != *"/wiki/"* ]] && exit 0

broken=()
while IFS= read -r link; do
  base="${link#\[\[}"; base="${base%\]\]}"; base="${base%%|*}"; base="${base%%#*}"
  for path in "$base" "concepts/$base" "entities/$base" "sources/$base" "questions/$base" "plan/$base"; do
    [ -f "$DROID_PROJECT_DIR/wiki/${path}.md" ] && continue 2
  done
  broken+=("$link")
done < <(grep -oE '\[\[[^]]+\]\]' "$file")

if [ ${#broken[@]} -gt 0 ]; then
  echo "{\"systemMessage\": \"Broken wikilinks in $(basename "$file"): ${broken[*]}\"}"
fi
```

#### `format-on-edit.sh` — language-aware formatter

Detects extension; runs the canonical formatter; writes back. Common entries:

- `.ts` / `.tsx` / `.js` / `.jsx` → `prettier --write`
- `.rs` → `rustfmt`
- `.py` → `ruff format` or `black`
- `.go` → `gofmt -w`
- `.json` → `prettier --write`

If no formatter is available for the extension, exit 0 silently.

### Optional hooks

- **`memory-capture.py`** — scans recent edits/commits for "decision-shaped" content (ADR creation, status change, error fix) and proposes adding to `.factory/memories.md`. Off by default; opt in when noisy.
- **`pre-commit`** — local guard that re-runs format + lint + typecheck before allowing the commit. The agent does NOT bypass this hook (`--no-verify` is forbidden).
- **`post-commit`** — appends to `wiki/log.md` automatically (if not done manually).

### Hook configuration

In `.factory/settings.json` (or runtime equivalent):

```jsonc
{
  "hooks": {
    "post_tool_use": [
      { "matcher": "Create|Edit|ApplyPatch", "command": ".factory/hooks/post-edit.sh" }
    ]
  }
}
```

### What hooks must NOT do

- **Block edits** — hooks emit `systemMessage`; they never refuse the edit. The agent decides what to do with the feedback.
- **Modify files outside the edited one** — except `format-on-edit.sh` writing back the formatted version of the same file.
- **Require network access** — hooks must run offline.

---

## 9. Agent workflow — how the agent actually builds this

The structure above is the artifact. The workflow below is how the agent gets there.

### The parallel-agent dispatch pattern

When work decomposes into independent pieces (no shared state, no sequential deps), the agent dispatches multiple sub-agents in parallel. **Always in a single message** with multiple Agent tool calls — never one-by-one.

Common dispatch shapes:

- **Master + N detail agents** — the lead agent writes a master overview, then dispatches N agents in parallel for the deep-dive sections. Each sub-agent's output goes to a different file (no collision).
- **Layer-batched dispatch** — for the package layer, dispatch one agent per layer (L0..L5). Each writes the READMEs for its layer's packages.
- **Range-batched dispatch** — for per-ID detail blocks, dispatch one agent per ID range (BB-001..040, BB-041..080, etc.).

### Output-token discipline

Sub-agents have output token caps (typically ~8K). Long files MUST be chunked:

1. **Seed Write**: frontmatter + intro + first 1–2 sections (~150 lines). Include a stable trailing marker like `<!-- END -->`.
2. **Edit-append**: each subsequent section is its own Edit call inserting BEFORE the `<!-- END -->` marker.
3. **Each Write or Edit must produce ≤ 120 lines** of output.
4. **Do not re-read the file between Edit calls** — the runtime tracks file state.

Communicate this to dispatched sub-agents in their prompts. **Strict chunking rules are mandatory for files > 400 lines.**

### When to dispatch vs do directly

| Situation | Approach |
|---|---|
| Single focused doc < 400 lines | Lead agent writes directly |
| Survey question, intermediate output you won't need again | Fork (Agent without subagent_type) |
| Multiple independent files | Parallel sub-agent dispatch |
| Long doc with structured sections | Sequential Edit-append, one section per call |
| Architectural decision needing deep think | Lead agent writes, no dispatch |
| Cross-checking / second opinion | Dispatch separate agent for fresh eyes |

### Dispatch prompt structure

Every dispatched sub-agent prompt includes:

1. **What to do** (1–2 sentences)
2. **Read first** (explicit file paths for context)
3. **Files to write** (explicit absolute paths, one per Write call)
4. **Per-file content guidance** (1–2 paragraphs per file)
5. **STRICT RULES**: chunking, ≤ 120 lines per call, no other files, no git
6. **REPORT BACK**: what to summarise (file paths, line counts, hardest decision, follow-ups)

Sub-agents do not commit, do not git push, do not lint. The lead agent handles those after all sub-agents return.

### Synthesis pattern

After parallel dispatch:

1. Verify file inventory (`find ... | wc -l`, `wc -l` per file)
2. Run lint (broken-wikilinks scanner across the wiki)
3. Append a synthesis entry to `wiki/log.md` describing what changed
4. Commit (single conventional-commit message; co-author the agent)
5. Push only if explicitly requested

### Verification before claiming "done"

Before reporting work complete, the agent runs:

- Lint (or whatever the project's "is this self-consistent" check is)
- Type-check (if a typed language)
- Test (if tests exist)
- Visual / functional check (if UI was touched — see §10 verification-first)

The agent surfaces failures as "blockers" not "done". `STATUS.md` tracks blockers explicitly.

### Anti-patterns to avoid

- Writing a 1,500-line file in one Write call (will hit output cap)
- Dispatching sub-agents without explicit `STRICT RULES` (they will collide / overrun)
- Reading a file between Edit-appends (no need; runtime tracks state)
- Committing before lint runs
- Claiming "done" without explicit verification evidence
- Using `git push --no-verify` to bypass hooks

---

## 10. Verification-first principle

**Verification at user-level is the default, not a step you remember to add.** The single most important architectural principle. Every project built from this template has this baked in from day one.

### The principle

> The harness refuses to call any work "done" until verification has run and returned a PASS verdict.

Not a recommendation. A hard gate. A package or feature without verification cannot ship.

### The 7-layer defense-in-depth verification stack

Every PASS verdict survives all 7 layers (or as many as apply):

| # | Layer | Catches |
|---|---|---|
| 1 | Static | Surface errors (types, lint, format, secrets, LSP) |
| 2 | Unit + property | Functional correctness of units |
| 3 | Integration | Cross-component contracts |
| 4 | End-to-end user-flow | "App appears to work but breaks for real users" |
| 5 | Behavioural fingerprinting | Regressions binary pass/fail misses |
| 6 | Mutation testing | Tests-that-don't-test (break code, verify tests FAIL) |
| 7 | Trace audit | Agent lying about what it did (claimed vs actual diffs) |

Any FAIL on any layer is a hard block. Project-specific implementations may add layers; layers may be omitted only if the failure mode is provably impossible for that target.

### The 4-tier judge stack

When LLM judgement is needed for grading, use a cost-tiered stack — never call frontier models on every action:

| Tier | What | When used |
|---|---|---|
| J0 | Deterministic graders (exit codes, schemas, status APIs) | Whenever ground truth exists |
| J1 | Distilled small judge (Phi-3-mini / Llama-3.1-8B per rubric) | Production: every action |
| J2 | Open-source structured judge (Prometheus 2 / equivalent) | Batch / nightly evals |
| J3 | Frontier spot-check (Opus / GPT-frontier) | 1% sampling, quarterly calibration |
| J4 | Pairwise + self-consistency voting | Version comparisons + oracle-less validation |

**Architectural rule (non-negotiable)**: the model that generated the artifact must not grade it. Use a dedicated validation model — both more accurate AND cheaper.

### 4 anti-gaming primitives

These prevent the agent from passing its own tests by gaming the test surface:

| | Rule | Why |
|---|---|---|
| AG-1 | Snapshot test files before agent run; restore before grading | Stops "I modified the tests to pass" |
| AG-2 | Compare claimed actions vs actual diffs | Catches lying about tool results |
| AG-3 | Deliberately break code; verify tests FAIL | Closes "no real tests = all pass" tautology |
| AG-4 | Every E2E assertion combines UI-text + server-state | Eliminates the #1 false-pass mode |

### Sandbox tiers (where verification runs)

Tiered to balance speed and isolation:

- **S0** (~seconds): Headless container with no native rendering — fastest, default for most runs
- **S1** (~tens of seconds): Container with display + input simulation — for native GUI without WebView
- **S2** (~half-minute): MicroVM with kernel isolation — for malicious-persona runs and untrusted code
- **S3** (~minutes): Real VM, including self-hosted per-OS runners — for top-level mission validation

Auto-selected from manifest; per-mission overrides allowed with audit.

### Personas — verify AS a configurable user

Verification drives the app as a person, not as a script. Personas vary timing, mistake rates, viewport, language. Standard set: novice, expert, distracted, malicious, mobile, edge-case. The same scenario as "novice" vs "expert" should produce **different verdicts** — if it doesn't, your verification isn't testing what users actually do.

### Recording → replay → calibration

Every verification session is recorded by default. Recordings drive three feedback loops:

- **Replay** — re-run a recording against a new build to detect regression
- **Mutation testing** — apply code mutations + replay + verify tests fail
- **Calibration dataset** — production failures become labelled training data for judge retraining

Recording format: intent JSONL (runner-agnostic) + runner-specific trace (CDP / screenshot stream / PTY / HTTP log) + state snapshots + RNG seed for deterministic replay.

---

## 11. Phasing model

The build plan is phased. Each phase has explicit packages, explicit done criteria, and explicit gates to the next phase.

### Phase template

| Phase | Duration | Goal | Packages new in this phase | Done criterion |
|---|---|---|---|---|
| **P0 spikes** | 1–2 wk | De-risk unknowns | none (spike tasks only) | All spikes PASS; pre-P1 ADRs in place |
| **P1 MVP** | 4–6 wk | Smallest version that doesn't crash | L0 + L1 + minimum L4 verification slice | First real target runs 24h without crash; returns a PASS verdict |
| **P2 Delegation** | 3–4 wk | Bounded fan-out for parallel work | L2 (subagents, recursive workers, knowledge objects) | First multi-file task solved with delegation |
| **P3 Quality+Recovery** | 3–4 wk | Survive restarts; catch regressions | Recovery primitives; full verification stack | Resume after kill -9; all 7 verification layers live |
| **P4 Mission** | 4–6 wk | Multi-day autonomous missions | L3 (mission state machine, eval, A/B) | One 72-hour mission with N human checkpoints |
| **P5 Auto-improvement** | open-ended | Harness improves itself | Meta-loop (proposal generator + A/B) | A/B loop produces measurable improvement / week |

Total to production-ready (P4): typically 14–20 weeks for 1 full-time engineer.

### P0 spikes — the pre-Week-1 experiments

Before any package code ships, run **3–5 spike experiments** that de-risk the biggest unknowns. Each spike is ~1 day. Each produces:

- A findings page at `wiki/spikes/<spike-name>.md`
- A single PASS / FAIL conclusion
- Any follow-up idea IDs

Common spike categories:

| Spike kind | What it answers |
|---|---|
| Runtime attach | Can our verification framework attach to the chosen runtime / language? |
| Sandbox stand-up | Does our sandbox tier reproduce in our environment? |
| SDK skeleton | Does the embedded test-mode SDK compile + open its control socket? |
| External dep probe | Does the planned external component have the API we expect? |

**Spikes are not the same as P1 work.** They produce findings, not shipping code. If a spike fails, the affected package design must be revisited before P1.

### Phase gate pattern

Each phase ends with explicit go/no-go criteria. Document in `PHASES.md`:

```markdown
### P<N> done criteria
- [ ] <package>: <observable check>
- [ ] <package>: <observable check>
- [ ] Verification: a real target passes all active layers
```

Don't advance to P<N+1> until P<N> done is checked off.

---

## 12. Setup checklist — concrete steps for a fresh repo

Execute these in order. Each step is a discrete commit.

### Step 1 — Repository init
```bash
git init <project-name> && cd <project-name>
echo "# <project-name>" > README.md
echo ".env*" > .gitignore
echo "node_modules/" >> .gitignore
echo "target/" >> .gitignore
echo ".DS_Store" >> .gitignore
git add . && git commit -m "Initial repo"
```

### Step 2 — Agent-runtime scaffold
Create `AGENTS.md`, `CLAUDE.md`, `.factory/{rules,skills,hooks}/`, `.factory/settings.json`, `.factory/memories.md`. Copy the rule files from this spec's appendix.

### Step 3 — Wiki scaffold
```bash
mkdir -p wiki/{raw,sources,entities,concepts,questions,IDEAS-details,plan/{adr,packages,spikes}}
```
Then author `wiki/SCHEMA.md`, `wiki/index.md`, `wiki/log.md` (empty), `wiki/PLAN.md`, `wiki/IDEAS.md` (empty board), `wiki/STATUS.md`.

### Step 4 — Hook scaffold
Create `.factory/hooks/post-edit.sh`, `wiki-lint.sh`, `format-on-edit.sh` (executable). Wire in `.factory/settings.json`.

### Step 5 — Vision + failure modes
Author `wiki/PLAN.md` with:
- 1-paragraph vision
- 5–10 named long-running failure modes
- Empty package table (filled in Step 7)
- 5-phase plan template
- Top N risks
- Open questions list

### Step 6 — Initial idea brainstorm
Author `wiki/IDEAS.md` with the project's idea-board structure. Add 10–30 starter ideas grouped by source/topic. Each has Effort × Impact rating.

### Step 7 — Package decomposition
With the failure modes in hand, decompose into 15–30 packages across 4–6 layers.

For each package:
```bash
mkdir -p wiki/plan/packages/<package-name>/adr
```

Write the 4 master docs:
- `wiki/plan/packages/README.md`
- `wiki/plan/packages/ARCHITECTURE.md`
- `wiki/plan/packages/INTEGRATION.md`
- `wiki/plan/packages/PHASES.md`

Then dispatch parallel sub-agents to write per-package READMEs (one agent per layer; see §9 for the dispatch pattern).

### Step 8 — Verification strategy
Author `wiki/plan/verification-strategy.md` with the 7-layer stack, 4 anti-gaming primitives, judge stack, sandbox tier model — adapted to the project's specific target type (web / desktop / CLI / API).

### Step 9 — Project-level ADRs
Author 5–10 project-level ADRs for the cross-cutting decisions. Minimum set:
- adr-001: Runtime technology choice
- adr-002: Sandbox / isolation scope
- adr-003: State store
- adr-004: (project-specific big choice)
- adr-005: Cost-accounting granularity
- adr-006: Hook ordering (canonical sequence per event)
- adr-007: (project-specific network / security policy)

### Step 10 — Per-package ADRs
For each package, identify 1–3 open architectural questions and author ADRs. Dispatch one sub-agent per layer to handle the bulk (see §9).

### Step 11 — Per-ID detail blocks
For ideas that have graduated past "table row", write detail blocks in `wiki/IDEAS-details/<batch-name>.md`. Dispatch sub-agents per batch.

### Step 12 — STATUS.md
Author `wiki/STATUS.md` summarising current state, blockers, sign-off requirements, architectural blast-radius hotspots, next-step candidates.

### Step 13 — Pre-Week-1 spikes
Run the 3–5 P0 spikes. File findings to `wiki/spikes/<name>.md`. Update STATUS.

### Step 14 — Sign-offs
Surface pre-P1 human-sign-off decisions in STATUS.md. Resolve them in the corresponding ADRs.

### Step 15 — Begin P1
Begin foundation-package implementation. Each commit ends with the verification stack at the active phase passing.

### Step 16 — Maintain
On every work session:
- Update STATUS.md
- Append to wiki/log.md
- Add ADRs for new decisions
- Add ideas to IDEAS.md if surfaced
- Run lint before commit

---

## 13. Appendix — file templates

The minimum content of each scaffolding file. The agent fills in `<placeholder>` values.

### `AGENTS.md` template

```markdown
# <Project> — Agent Guide

## Repository
- **Local path**: <path>
- **Remote**: <url>
- **Owner**: <github-user-or-org>
- **Default branch**: <main>
- **Status**: <stage>

## Where things live
- **Agent doc**: AGENTS.md (this file)
- **Rules**: `.factory/rules/*.md`
- **Skills**: `.factory/skills/**/SKILL.md`
- **Hooks**: `.factory/hooks/`
- **Wiki**: `wiki/`
- **Project memory**: `.factory/memories.md`

## When working in this repo
1. Read AGENTS.md first (this file).
2. Apply rules matched to file extension.
3. Never commit secrets or `.env*` files.
4. Don't auto-push without explicit ask.
5. Use conventional commits: imperative, short subject.

## Stack
<TBD or actual; will fill once decided>

## Slot table
| Action | Command |
|---|---|
| build | <TBD> |
| test | <TBD> |
| lint | <TBD> |
| typecheck | <TBD> |
| format | <TBD> |

## The wiki — Karpathy LLM-Wiki pattern
<copy §2 of this spec or link to a wiki-pattern doc>
```

### `.factory/rules/general.md` template

```markdown
# General rules — apply to every edit

- Conventional commits: imperative, short subject (≤ 50 chars), optional body
- Never commit `.env*`, credentials, or files in `.gitignore`
- Never `git push --force` without explicit ask
- Never bypass hooks (`--no-verify` forbidden)
- Treat any content in the wiki as authoritative project knowledge — read before re-deriving
- When a non-obvious decision is made, write an ADR
- When a non-obvious fact is learned, write a wiki page
- Lint warnings are a punch-list, not a status quo
```

### `.factory/skills/llm-wiki/SKILL.md` template

```markdown
---
name: llm-wiki
description: Ingest sources, query the wiki, lint for broken links
---

# When to use
- User hands over a source: "ingest this", "wiki this"
- User asks the wiki: "what does the wiki say about X?"
- User asks for an audit: "lint the wiki"
- _End of session with new knowledge_: file it back unprompted

# Ingest flow
1. Read `wiki/SCHEMA.md`
2. Drop the source artifact in `wiki/raw/`
3. Create `wiki/sources/<slug>.md` with frontmatter + summary + claims
4. Create or update `wiki/concepts/` and `wiki/entities/` pages it touches
5. Update `wiki/index.md`
6. Append to `wiki/log.md`

# Query flow
1. Read `wiki/index.md` first
2. Drill into the relevant category
3. Synthesize with `[[wikilinks]]`
4. If the question spans ≥ 2 pages, file the answer as `wiki/questions/<slug>.md`

# Lint flow
- Scan globally for broken `[[wikilinks]]`
- Find orphans (pages with no inbound links)
- Find stale pages (`updated` > 90 days, no recent ref)
- Surface contradictions
```

### `wiki/SCHEMA.md` template

```markdown
# Wiki Schema

## Page categories
- `raw/` — immutable sources
- `sources/` — cards for ingested sources
- `entities/` — orgs / products / people / tools
- `concepts/` — ideas / patterns / techniques
- `questions/` — resolved Q&A

## Required frontmatter
<copy from §2 of the spec>

## Filename convention
- lowercase-kebab-case.md

## Wikilink convention
- `[[category/slug]]` or `[[category/slug|display text]]`
- Without `.md` suffix

## Operations
- Ingest, Query, Lint — see `.factory/skills/llm-wiki/SKILL.md`
```

### `wiki/index.md` skeleton

```markdown
# Wiki Index

The catalog of every page. Updated on every ingest.

## Sources
<empty until first ingest>

## Entities
<empty>

## Concepts
<empty>

## Questions
<empty>

## Plan
- [[PLAN]] — master plan
- [[STATUS]] — current state
- [[IDEAS]] — idea board

---
_See `SCHEMA.md` for conventions. The LLM owns this file — humans read it; the LLM writes it._
```

### `wiki/PLAN.md` skeleton

```markdown
---
title: <Project> — Master Plan
type: plan
updated: YYYY-MM-DD
---

# <Project> — Game Plan

## Vision
<1 paragraph>

## The N long-running failure modes
| # | Failure mode | Primary ideas that address it |

## Architecture — N packages, M layers
<table>

## The 5-phase build plan
| Phase | Goal | Packages | Duration | "Done" |

## Top N risks
1.

## What "done" looks like per phase
### P1 — [ ] criterion
### P2 — [ ] criterion

## Open questions (resolve before P1)
1.

## Idea-board cross-reference
See [[IDEAS]].
```

### `wiki/STATUS.md` skeleton

```markdown
---
title: <Project> — Project Status & Blocker Map
type: plan
updated: YYYY-MM-DD
---

# Where We Are — and What's Blocked on What

## Current state — at a glance
| Bucket | Count | Status |

## What ships in P<N> — packages

## Pre-P<N> human-sign-off requirements
1. ⬜ <decision>
2.

## Pre-P<N> implementation-blocking ADR gaps
1.

## Architectural blast-radius hotspots
1.

## P<N>-elevation candidates — actionable right now
- <ID> — <title>

## Open documentation backlog (not blocking)

## What's intentionally out of scope (right now)

## The one-sentence current-state summary
> <one sentence>
```

---

## 14. The non-negotiable principles (the project's spine)

The spec encodes seven principles that hold across every project built from this template. Violate any of them and the pattern degrades; honor them and the pattern compounds.

1. **The wiki is the agent's long-term memory.** Anything worth remembering goes to the wiki. Don't let knowledge vanish into chat history.

2. **Every failure mode has an owner package.** When a failure happens in production, name the package responsible. If no package owns it, that's a design bug.

3. **Verification at user-level is the default.** No work is "done" without a PASS verdict from the active verification layers. The harness enforces this; the agent does not opt out.

4. **The model that generated must not grade.** Always use a dedicated validation model at a lower cost tier. More accurate AND cheaper.

5. **ADRs capture every non-trivial decision.** Decisions left in chat history get re-litigated. Decisions in ADRs compound.

6. **Hook ordering is canonical and enforced.** Hook subscribers register; pi-daemon (or equivalent) refuses to start on non-canonical registration. Silent priority collisions cannot happen.

7. **Parallel agent dispatch with strict chunking.** Large work is dispatched as parallel sub-agents to non-overlapping files; each sub-agent uses Edit-append with ≤ 120 lines per call.

---

## 15. Anti-patterns to refuse

These will look reasonable and they will erode the pattern:

| Anti-pattern | Why it erodes |
|---|---|
| One giant ADR doc with many decisions | Decisions become un-citeable; reversing one bleeds into others |
| Re-deriving knowledge on every query instead of filing it back | Defeats the wiki; you're back to ad-hoc RAG |
| Hand-authoring 200 detail blocks one by one | Use parallel dispatch; the lead agent shouldn't be a bottleneck |
| "Just write tests later" | The verification stack is upstream of P1; missing it ships broken |
| "We'll figure out hook order at runtime" | Silent collisions. Adopt the fatal-startup-error pattern from day 1 |
| Skipping pre-Week-1 spikes "because the plan looks good" | Spikes de-risk; the plan is a hypothesis until they pass |
| Allowing `--no-verify` to bypass hooks | Hooks exist precisely to catch the failures you'd otherwise miss |

---

## How to hand this spec to an agent

Drop this file into a fresh repo as `PROJECT-TEMPLATE-SPEC.md` (or paste its contents into the first prompt). Then say:

> Read PROJECT-TEMPLATE-SPEC.md end to end. Then execute the Setup Checklist (§12) one step at a time, asking me for project-specific values (project name, vision, target type, language stack) as needed. Use the file templates in §13 verbatim where applicable. Use the parallel dispatch pattern from §9 for any step that decomposes naturally.

The agent will produce a fully-scaffolded, deeply-planned, agent-friendly repo in approximately one work session.

---

_End of spec._

