# General rules — apply to every edit

- Conventional commits: imperative, short subject (≤ 50 chars), optional body.
- Never commit `.env*`, credentials, or files in `.gitignore`.
- Never `git push --force` without explicit ask. Never push to main/master without ask.
- Never bypass hooks (`--no-verify` forbidden).
- Treat any content in `wiki/` as authoritative project knowledge — read before re-deriving.
- When a non-obvious decision is made, write an ADR at `wiki/plan/adr/`.
- When a non-obvious fact is learned, write a wiki page (sources/entities/concepts/questions).
- Lint warnings are a punch-list, not a status quo.
- Invoke `skill-discovery` BEFORE any other tool call. If no skill matches, invoke
  `skill-creator` to make one rather than improvising.
- Surface contradictions; never paper them over.
- When dispatching parallel sub-agents, follow `skills/parallel-dispatch/SKILL.md` —
  strict ≤120-line chunking, explicit file ownership, no overlap.
- Verification gate: no work is "done" until the active verification layers return PASS.
- The model that generated an artifact must not grade it. Use the judge stack in
  `skills/verification-first/`.
