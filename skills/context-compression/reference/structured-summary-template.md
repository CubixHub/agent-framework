# Structured summary template

Save as `.agent-os/context.md` and update by MERGING new content. Never regenerate.

```markdown
---
title: <project> — Session context
type: context
updated: YYYY-MM-DD HH:MM
session_id: <slug or PM-issue-id>
---

# Session context

## Intent
<2-3 sentences: what we are trying to accomplish in this session.>

## Decisions made (with rationale)
- <decision> — <one-line why>. (ADR if any: [[adr-NNN-...]])
- <decision> — <why>.

## File modifications
| Path | Status | Nature of change |
|---|---|---|
| `src/foo.ts` | edited | refactored to extract `bar()` helper; preserved external API |
| `tests/foo.test.ts` | created | covers new branch in `bar()` |
| `wiki/concepts/zustand-pattern.md` | created | ingested via wiki-curator |

## Open questions
1. <question> — awaiting <user / scrutinizer / parent-ai>
2. <question> — blocked on <thing>

## Next steps
1. <immediate todo>
2. <next>
3. <after that>

## Tool calls of note
Only list calls whose RESULT is needed for continuation. Don't dump the transcript.
- `Grep "useStore"` → 14 occurrences, 12 in `src/components`.
- `Bash "npm test"` → 1 fail in `auth.test.ts:42`.

## Don't lose this
- <critical fact or insight that could vanish>
```

## Merging rules

When compressing a new span:
1. Read the existing summary.
2. Summarize the new span into the same 6 sections.
3. For each section: combine the two, deduplicating identical bullets.
4. Trim aggressively: anything no longer relevant moves to "archive" or to the wiki.
5. Update `updated:` frontmatter.

Items that grow unbounded → file as wiki pages, not summary entries.
