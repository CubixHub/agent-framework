# Wiki Schema — read before any wiki operation

Karpathy LLM-Wiki pattern: persistent, compounding markdown knowledge base
instead of RAG over raw text. The wiki is the agent's long-term memory.

## Page categories

| Folder         | Contents                                  | Mutability       |
|----------------|-------------------------------------------|------------------|
| `raw/`         | Immutable source files (PDFs, transcripts, screenshots) | **Never modify** |
| `sources/`     | One card per ingested source              | Agent writes     |
| `entities/`    | Orgs, products, people, tools             | Agent writes     |
| `concepts/`    | Ideas, patterns, techniques               | Agent writes     |
| `questions/`   | Resolved Q&A spanning ≥ 2 pages           | Agent writes     |
| `IDEAS-details/` | Per-ID idea detail blocks (one file per batch) | Agent writes |
| `plan/`        | Project planning (ADRs, packages, spikes) | Agent writes     |
| `spikes/`      | Findings from P0 spike experiments        | Agent writes     |

## Required frontmatter (every wiki page)

```yaml
---
title: <short human title>
type: source | entity | concept | question | adr | plan | run
tags: [kebab-case, list]
updated: YYYY-MM-DD
sources: [optional wikilinks]
---
```

## Filename convention

- All lowercase, hyphenated: `wikilink-target-slug.md`.
- Filename must match the slug used in `[[wikilinks]]`.

## Wikilinks

- `[[category/slug]]` or `[[category/slug|display]]`.
- No `.md` suffix (lint tools treat `foo.md` and `foo` as different targets).
- Link liberally — broken links are TODO markers, not errors.

## Citations

- Every non-trivial claim cites its source via `[[sources/<slug>]]`.

## Contradictions — surface, don't paper over

```
> ⚠ Contradicts [[other-page]] as of YYYY-MM-DD — <reason>
```

## The three mandatory index files

- `wiki/index.md` — catalog of every page (agent maintains on every write).
- `wiki/log.md` — append-only chronological log of wiki operations.
- `wiki/PLAN.md` — the master project plan.

## Operations the agent supports

| Trigger                                        | Workflow |
|------------------------------------------------|----------|
| "ingest this", "wiki this", URL handed over   | Ingest   |
| "what does the wiki say about X?"             | Query    |
| "lint the wiki"                                | Lint     |
| _End of session with new knowledge_           | Unprompted file-back |

See `.agent-os/skills/llm-wiki/SKILL.md` for the exact ops.
