# Query flow

## Input
- A natural-language question. e.g. "what does the wiki say about X?".

## Step-by-step

1. **Index first**: read `wiki/index.md`. Identify candidate pages (entities,
   concepts, questions, sources).

2. **Drill**: read the candidate pages. Follow `[[wikilinks]]` one hop deep.

3. **Synthesize**: write the answer in prose, citing every non-trivial claim via
   `[[category/slug]]` (no `.md` suffix). Keep it tight.

4. **File-back rule**: if the answer spans ≥ 2 wiki pages, save the synthesis as
   a `wiki/questions/<slug>.md`:
   ```markdown
   ---
   title: <question paraphrased>
   type: question
   tags: [<topic-tags>]
   updated: YYYY-MM-DD
   ---

   # <question>

   ## Short answer
   <2-3 sentences>

   ## Sources
   - [[sources/<slug>]] — <what it contributed>
   - [[concepts/<slug>]] — <what it contributed>
   ```

5. **Update index** + `wiki/log.md`.

## When NOT to file as a question
- Trivial questions answered by one page.
- Questions already covered by an existing `wiki/questions/<slug>.md` —
  update the existing one instead of creating a duplicate.

## Avoid
- Answering from chat history instead of the wiki. If chat-history has a fact
  the wiki doesn't, file it BEFORE answering.
- Skipping citations. "I think we decided X" is unverifiable. "We decided X
  [[questions/...]]" is verifiable.
