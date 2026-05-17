# Skill Authoring — Worked Examples

Two complete skills. One rigid, one flexible. Each shows the full SKILL.md body and a representative reference file.

---

## Example 1 — Rigid: `test-driven-development`

A process skill. The order is mandatory; deviation breaks the discipline.

### Frontmatter

```yaml
---
name: test-driven-development
description: Drive feature work and bug fixes with red-green-refactor when the user asks for TDD, mentions tests-first, or fixes a bug. Produces a failing test, minimal implementation, refactored code, and a mutation-test check at the end.
---
```

### Body structure (excerpt)

```markdown
# When to use

- User says "TDD", "test-first", "red-green-refactor".
- User reports a bug and you are about to fix it. (Bug fixes start with a failing test.)
- New behaviour is being added that crosses a public boundary.

Do not use for: throwaway prototypes, single-file scripts, exploratory spikes.

# How to execute

1. **Plan**: list the behaviours to test (3–7, not 30). Get user approval before coding.
2. **Tracer bullet**: write ONE test that fails. Confirm it fails for the *right reason* (not a compile error).
3. **Green**: write the minimum code to pass. No speculation.
4. **Loop**: repeat tracer → green for each remaining behaviour. One at a time. Vertical slices, never horizontal.
5. **Refactor**: only after all tests pass. Run tests after every refactor step.
6. **Mutation check**: introduce a deliberate fault. Tests MUST fail. If not, the tests are crap; fix them.

# Quality bar

- [ ] Every test exercises a public interface, not an internal function.
- [ ] No mocks of internal modules.
- [ ] Mutation check ran and tests caught the fault.
- [ ] Test names follow "should X when Y" format.

# Anti-patterns

- Writing all tests first, then all implementation (horizontal slicing — produces fake tests).
- Adding speculative code beyond what the current test requires.
- Skipping mutation check ("they passed, must be fine").
- Mocking internal collaborators to make a test compile.
```

### Notes on why this works

- Description starts with a verb, lists 3 triggers, ends with deliverable.
- Steps are ordered and mandatory. Each has a single deliverable.
- Anti-patterns name specific failure modes with reasons.
- Reference would split into `red-green-refactor.md`, `mutation-testing.md`, `interface-design.md`.

---

## Example 2 — Flexible: `brainstorming`

An exploration skill. The structure bounds the work; the path is free.

### Frontmatter

```yaml
---
name: brainstorming
description: Explore intent, requirements, and design before writing code when the user asks for a new feature, a refactor, or a behaviour change. Outputs a 5-question discovery dialogue and a one-page design sketch, never code on the first pass.
---
```

### Body structure (excerpt)

```markdown
# When to use

- User asks for a new feature ("build me X", "add Y").
- User asks for a refactor or rewrite.
- User describes a problem without proposing a solution.

Do not use for: bug fixes (use `diagnose`), trivial edits (one-line changes), or follow-up
turns where the design is already settled.

# How to execute

Ask the 5 framing questions, in order. The user may answer in any granularity; you adapt
follow-ups. Do not write code in this phase.

1. **Intent**: what is the user actually trying to achieve? (Not the feature — the goal.)
2. **Users**: who experiences this? Novice / expert / both? Internal / external?
3. **Constraints**: what is non-negotiable? (Latency, cost, privacy, compatibility.)
4. **Alternatives**: what is the buy-vs-build space? Existing libraries?
5. **Done**: how will the user know it works? Observable criteria, not vibes.

After the dialogue, produce a one-page sketch with these sections:
- Problem (2–4 sentences)
- Approach (3–6 sentences)
- Non-goals (what we are NOT building)
- Open questions (numbered)

End by asking: "Approve this sketch, or iterate?" Do not proceed until approval.

# Quality bar

- [ ] All 5 questions answered (or explicitly deferred).
- [ ] Sketch fits on one page.
- [ ] Non-goals section names ≥2 things this skill is NOT building.

# Anti-patterns

- Writing code before the sketch is approved.
- Skipping a framing question because "the user already said".
- Producing a 5-page sketch (it must fit on one page; details go in ADRs after approval).
- Asking the user to "tell me everything you want" — they don't know yet. The questions exist to extract it.
```

### Notes on why this works

- Description names exactly when to use (3 trigger types) and the deliverable shape.
- Procedure has a structure (5 questions, one-page output) but no rigid ordering of follow-ups.
- Anti-patterns refuse the obvious lazy paths (writing code early, ignoring the structure).
- Reference would split into `framing-questions.md`, `sketch-template.md`.

---

## Take-aways

- Both skills are roughly the same length (≈100 lines of body). Length is not the difference.
- Both have ordered structure. The rigid one orders execution; the flexible one orders prompts.
- Both have a non-empty anti-patterns block.
- Neither hedges. "Do not proceed until approval." Not "consider waiting for approval."
