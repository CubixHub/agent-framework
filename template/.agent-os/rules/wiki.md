# Wiki rules — Karpathy LLM-Wiki conventions

The wiki is the agent's long-term memory. Read `wiki/SCHEMA.md` before any wiki edit.

## Page categories
- `wiki/raw/`        — immutable source files (PDFs, transcripts). NEVER MODIFY.
- `wiki/sources/`    — one card per ingested source.
- `wiki/entities/`   — orgs, products, people, tools.
- `wiki/concepts/`   — ideas, patterns, techniques.
- `wiki/questions/`  — resolved Q&A spanning ≥ 2 pages.

## Required frontmatter (every page)
```yaml
---
title: <short human title>
type: source | entity | concept | question
tags: [kebab-case, list]
updated: YYYY-MM-DD
sources: [optional wikilinks to source pages]
---
```

## Filename convention
- `lowercase-kebab-case.md`.
- Slug should match the wikilink reference.

## Wikilinks
- `[[category/slug]]` or `[[category/slug|display text]]`.
- Without `.md` suffix.
- Link liberally — a link to a missing page is a TODO marker.

## Citations
- Every non-trivial claim cites a source via `[[sources/slug]]`.

## Contradictions
- Surface, don't paper over:
  ```
  > ⚠ Contradicts [[other-page]] as of YYYY-MM-DD — <one-sentence reason>
  ```

## Maintenance
- `wiki/index.md`: catalog of every page, agent maintains on every write.
- `wiki/log.md`: append-only chronological log of wiki operations.
- End-of-session unprompted file-back if new knowledge learned — don't let it vanish.
