---
name: llm-wiki
description: Maintain the Karpathy LLM-Wiki — ingest sources, answer queries, lint, file findings back to wiki/. Invoke on any "wiki this", "what does the wiki say about X", "lint the wiki", or end-of-session with new knowledge.
---

# When to use

- User hands over a source: "ingest this", "wiki this", URL or file dropped in.
- User asks the wiki: "what does the wiki say about X?", "what did we decide about Y?".
- User asks for audit: "lint the wiki", "find orphans", "find broken links".
- **End of any session with meaningful new knowledge** — file it back unprompted.
  Knowledge that vanishes into chat history is a defect.

# How to execute

## Step 0 — Always read first
Read `wiki/SCHEMA.md`. Conventions evolve; never assume.

## Step 1 — Ingest flow
See [reference/ingest-flow.md](reference/ingest-flow.md).
1. Drop the source artifact in `wiki/raw/<slug>.<ext>` (immutable).
2. Create `wiki/sources/<slug>.md` with frontmatter + summary + key claims.
3. Create or update `wiki/entities/` and `wiki/concepts/` pages this source touches.
4. Update `wiki/index.md`.
5. Append to `wiki/log.md` with date and changes.

## Step 2 — Query flow
See [reference/query-flow.md](reference/query-flow.md).
1. Read `wiki/index.md` first.
2. Drill into the relevant category.
3. Synthesize the answer using `[[wikilinks]]` to every cited page.
4. If the question spans ≥ 2 wiki pages, file the answer as
   `wiki/questions/<slug>.md` so future-you finds it without re-deriving.

## Step 3 — Lint flow
See [reference/lint-flow.md](reference/lint-flow.md).
1. Scan globally for broken `[[wikilinks]]` (use `.agent-os/hooks/wiki-lint.sh`).
2. Find orphans (pages with no inbound links).
3. Find stale pages (`updated` > 90 days, no recent ref).
4. Surface contradictions (callouts of the form `⚠ Contradicts [[other-page]]`).

## Step 4 — Cite, link, contradict
- **Cite every non-trivial claim**: link to the source via `[[sources/<slug>]]`.
- **Link liberally**: a link to a missing page is a TODO marker, not an error.
- **Surface contradictions**:
  ```
  > ⚠ Contradicts [[other-page]] as of YYYY-MM-DD — <one-sentence reason>
  ```
  Never silently resolve.

# Reference
- [reference/ingest-flow.md](reference/ingest-flow.md)
- [reference/query-flow.md](reference/query-flow.md)
- [reference/lint-flow.md](reference/lint-flow.md)
- [reference/wiki-schema.md](reference/wiki-schema.md)

# Anti-patterns (refuse)
- Re-deriving knowledge on every query instead of filing it back.
- Modifying `wiki/raw/` — it's immutable source material.
- Silently merging contradictions.
- Skipping `wiki/log.md` updates.
- Hand-authoring a `[[wikilink]]` to a page you didn't create or check.
