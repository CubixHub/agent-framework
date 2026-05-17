# Lint flow

## Goals
- Broken `[[wikilinks]]` → either create the missing target or fix the link.
- Orphan pages (no inbound links) → either link them in or delete.
- Stale pages (`updated` > 90 days, no recent ref) → review.
- Contradictions → surface them; never silently resolve.

## Step-by-step

1. **Broken wikilinks**: the post-edit hook
   `.agent-os/hooks/wiki-lint.sh` flags these on every edit. Periodically run
   a global pass:
   ```bash
   grep -rnE '\[\[[^]]+\]\]' wiki/ | while read -r match; do
     # parse target, check existence — see hook source for the algorithm
   done
   ```

2. **Orphans**: a page is an orphan if no other page links to it. Cross-check
   with `grep -rl "$slug" wiki/`. Decision per orphan:
   - Recently created? Add inbound links from related pages.
   - Old + unused? Move to an archive section in `wiki/log.md` or delete.

3. **Stale**: compare each page's `updated:` frontmatter to today.
   ```bash
   find wiki/ -name '*.md' -exec grep -l "updated:" {} \;
   ```
   For pages older than 90 days, check `git log -p` for whether the topic has
   evolved since. If yes, update; if no, leave.

4. **Contradictions**: search for the callout marker.
   ```bash
   grep -rn "⚠ Contradicts" wiki/
   ```
   For each: either resolve (one side wins, document why in an ADR) or leave
   (genuine open question, file as `wiki/questions/`).

5. **Log the lint**: append to `wiki/log.md`:
   ```
   ## YYYY-MM-DD — lint
   - broken: <N> (fixed: <M>, deferred: <K>)
   - orphans: <N> (linked: <M>, archived: <K>)
   - stale: <N> (refreshed: <M>, removed: <K>)
   - contradictions: <N> (resolved: <M>)
   ```
