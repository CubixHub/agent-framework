# Wiki schema — quick reference

## Page categories
| Folder | Type | Example slug |
|---|---|---|
| `raw/` | (immutable source) | `karpathy-llm-wiki-tweet.png` |
| `sources/` | source card | `karpathy-llm-wiki-tweet.md` |
| `entities/` | org/person/product/tool | `anthropic.md` |
| `concepts/` | idea/pattern/technique | `llm-wiki-pattern.md` |
| `questions/` | resolved Q&A | `why-not-rag-on-every-query.md` |

## Frontmatter
```yaml
---
title: <short human title>
type: source | entity | concept | question | adr | plan | run
tags: [kebab-case, tags]
updated: YYYY-MM-DD
sources: [optional wikilinks]
---
```

## Filename
- All lowercase.
- Hyphenated.
- Slug matches the wikilink target.

## Wikilinks
- `[[category/slug]]` or `[[category/slug|display text]]`
- No `.md` suffix.
- Link liberally.

## Citations
- Every non-trivial claim cites a source: `[[sources/<slug>]]`.

## Contradictions callout
```
> ⚠ Contradicts [[other-page]] as of YYYY-MM-DD — <reason>
```

## Mandatory index files
- `wiki/index.md` — catalog
- `wiki/log.md` — append-only operations log
- `wiki/PLAN.md` — master plan
- `wiki/STATUS.md` — current state
- `wiki/IDEAS.md` — backlog
- `wiki/SCHEMA.md` — this doc, but project-level
