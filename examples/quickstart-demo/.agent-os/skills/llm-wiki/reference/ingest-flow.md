# Ingest flow

## Input
- A URL, file path, paste-buffer of text, or screenshot.

## Step-by-step

1. **Identify**: figure out the slug. Lowercase kebab-case. E.g. "Karpathy's
   LLM-wiki tweet" → `karpathy-llm-wiki-tweet`.

2. **Land raw**: copy the source to `wiki/raw/<slug>.<ext>`.
   - For URLs: WebFetch and save the markdown form.
   - For PDFs: save the original.
   - For screenshots: save with `<slug>.png`.

3. **Write the source card**: `wiki/sources/<slug>.md`:
   ```markdown
   ---
   title: <one-line human title>
   type: source
   tags: [<topic-tags>]
   updated: YYYY-MM-DD
   url: <original URL if any>
   ---

   # <title>

   ## Summary
   <3-5 sentences>

   ## Key claims
   - <claim 1>
   - <claim 2>

   ## Related entities
   [[entities/<slug>]] ...

   ## Related concepts
   [[concepts/<slug>]] ...
   ```

4. **Touched entities**: for each org/person/product the source mentions, create
   or update `wiki/entities/<slug>.md`. Add a line citing this source.

5. **Touched concepts**: for each idea/pattern/technique, create or update
   `wiki/concepts/<slug>.md`. Add a line citing this source.

6. **Update index**: add the new source under `## Sources` in `wiki/index.md`.

7. **Log**: append to `wiki/log.md`:
   ```
   ## YYYY-MM-DD — ingest: <slug>
   - created: [[sources/<slug>]]
   - created/updated: [[entities/<slug>]]
   - created/updated: [[concepts/<slug>]]
   ```
