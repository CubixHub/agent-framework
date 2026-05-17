# Dispatch Prompt Template

Copy this into the sub-agent prompt. Fill in the bracketed placeholders. Do not remove sections.

```
You are a sub-agent in a [master+N | layer | range]-batched parallel dispatch.

## What to do
[1–2 sentences. The task. Plain language. No fluff.]

## Read first
Before writing, read these files for context:

- /absolute/path/to/spec.md  (the canonical spec — section [X.Y])
- /absolute/path/to/existing/sibling.md  (style reference)
- [add more as needed]

Do not read more files than listed. Anything else is scope creep.

## Files to write

Total: [N] files.

1. /absolute/path/to/file-1.md  (target line count: ~[X])
2. /absolute/path/to/file-2.md  (target line count: ~[X])
3. [etc.]

One Write call per file. No more files than listed.

## Per-file content guidance

### File 1: /absolute/path/to/file-1.md

[1–2 paragraphs: what goes in this file, what structure, what tone.
Reference the spec section if applicable. Name the key sections required.]

### File 2: /absolute/path/to/file-2.md

[Same shape as above.]

[...]

## STRICT RULES

Mandatory. Violation produces unusable output.

- **Chunking**: each Write or Edit call produces ≤120 lines of output. Files over 400 lines are written as: (a) Seed Write with frontmatter + intro + first 1–2 sections including a trailing `<!-- END -->` marker, then (b) Edit-append for each subsequent section, inserting before the marker.
- **Do not re-read** a file between Edit calls. The runtime tracks state.
- **No other files**. Do not create files not listed above. Do not edit files outside the write targets.
- **No git operations**. Do not commit. Do not push. Do not stage. The lead agent commits after all sub-agents return.
- **No lint, no test, no format**. The lead agent runs these after synthesis.
- **No invocations of other tools** beyond Read (for the files listed in "Read first") and Write/Edit (for the targets). No bash unless explicitly needed for the task.
- **Frontmatter** (if applicable to the target): every markdown doc starts with the project's standard frontmatter block. See [reference doc] for the schema.

## REPORT BACK

When complete, your final message lists:

- One line per file written: `<path>  (<line-count> lines)`
- The hardest design decision you made and why
- What you cut for time or budget and recommend as follow-up
- Any blockers you hit (truncation, missing context, ambiguity)

Keep the report ≤30 lines. The lead agent reads every report.
```

## Filling in the template

### Choosing line-count targets

- README / overview doc: 150–300 lines
- Per-package detail doc: 200–400 lines
- ADR: 80–200 lines
- Idea detail block: 30–60 lines per ID

If a target exceeds 400 lines, the sub-agent must chunk. Include the chunking instruction verbatim.

### Choosing "Read first" files

Only files the sub-agent strictly needs. Common entries:

- The spec section that defines the doc shape.
- One sibling doc that already exists, as a style reference.
- The frontmatter schema (if non-obvious).

Avoid dumping the entire spec. Sub-agents waste context if given too much; the lead has read everything, the sub-agent reads only what is specific to its task.

### Choosing the write target paths

Absolute paths. One per Write call. Confirm in the inventory step (post-dispatch) that all expected paths landed.

If two sub-agents end up with the same write target, the dispatch is wrong. Re-split.

## Example dispatch — three packages in parallel

```
Lead message:

  Agent call 1:
    prompt = template-with-substitutions(
      package = "auth",
      files = ["/path/wiki/plan/packages/auth/README.md", "/path/wiki/plan/packages/auth/adr/001.md"],
      sibling = "/path/wiki/plan/packages/storage/README.md")

  Agent call 2:
    prompt = template-with-substitutions(
      package = "billing",
      files = ["/path/wiki/plan/packages/billing/README.md", "/path/wiki/plan/packages/billing/adr/001.md"],
      sibling = "/path/wiki/plan/packages/storage/README.md")

  Agent call 3:
    prompt = template-with-substitutions(
      package = "audit",
      files = ["/path/wiki/plan/packages/audit/README.md", "/path/wiki/plan/packages/audit/adr/001.md"],
      sibling = "/path/wiki/plan/packages/storage/README.md")
```

All three in one message. The runtime parallelises.

## What the lead does after returns

The lead:

1. Reads each sub-agent's report.
2. Runs `wc -l` on the produced files. Sanity-checks against the target line counts. Truncation usually appears here.
3. Runs the project's lint / link-checker. Flags broken links and orphan files.
4. Appends a synthesis entry to the project's audit log.
5. Commits with a single conventional-commit message naming the dispatch.

If any sub-agent reported a blocker, the lead handles it directly — does not re-dispatch the failed sub-agent (which would burn another full dispatch cycle for one file).
