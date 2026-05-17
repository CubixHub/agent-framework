# Prompt Crafting (Tri-Platform)

> Applies to: Claude Code, Codex, Pi. Universal principles first, then per-CLI deltas, then a model-selection table. Rewrites Factory.ai's Prompt Crafting guide.

## Universal principles

Apply these regardless of CLI vendor.

1. **One ask per turn.** Multi-ask prompts get partial answers. If you have two questions, split them.
2. **Specific > general.** "Refactor `Auth.handleLogin` to use the new `Session` API" beats "clean up the auth module".
3. **State the success criterion.** "Done when `pnpm test` passes and the diff touches only `src/auth/`." The agent prioritizes what it can measure.
4. **Show the shape of the answer.** Show a sample output, a diff, a JSON schema — anything that pins down the format.
5. **Quote the source verbatim.** Pasting the exact error message beats describing it. Same for log lines, doc snippets, API responses.
6. **Reference, don't restate.** "Apply `.agent-os/rules/backend/python.md`" beats re-stating the rules in the prompt. Trust the entry-point doc chain.
7. **Plan before code on anything non-trivial.** Two passes (plan → critique → code) beats one pass + rework.

## Claude techniques

### XML tags for structure

Claude reads XML tags as semantic structure. Use them for any prompt with ≥ 2 sections:

```xml
<task>Refactor Auth.handleLogin to use Session.</task>
<context>
  The new API is in src/lib/session.ts. The old call site is at src/auth/login.ts:42.
</context>
<constraints>
  - Don't touch test files
  - Keep the function signature
</constraints>
<output>
  Diff only. No explanation.
</output>
```

### "Think through" for hard problems

Append `Think through your approach before writing code.` for non-trivial tasks. Claude will write a plan first; you can interrupt if the plan is wrong. Saves the round-trip of bad code → review → rewrite.

### Plan mode

`claude --mode plan` forces plan-first behavior across the session. See [Token efficiency](./05-token-efficiency.md).

## Codex / GPT techniques

### Role framing

Codex responds well to role framing at the top:

```
You are a senior backend engineer. You write idiomatic Python. You never introduce dependencies without justification.
```

Keep it terse — ≤ 3 sentences. Long role framings burn context without changing behavior.

### Numbered steps

For multi-step tasks, number the steps explicitly. GPT-family models follow numbered procedures more reliably than prose.

```
1. Read src/api/handlers.py.
2. Identify all routes that accept POST.
3. For each, add a `request_id` field to the logged payload.
4. Run pytest -q and report failures.
```

### Explicit output format

Tell Codex what to emit and what NOT to emit:

```
Output a single unified diff. No prose. No code fences.
```

## Pi techniques

Pi is the minimal one — fewer built-in conventions, more leverage from per-project config.

### SYSTEM.md customization

`~/.pi/SYSTEM.md` is Pi's role anchor. Customize per-domain:

```markdown
You are a coding harness operating in <project>. Read AGENTS.md before any tool call.
Prefer pnpm. Never push to main. Use the project's wiki at `wiki/` as long-term memory.
```

Per-project overrides go in `<project>/.pi/SYSTEM.md`.

### Leverage AGENTS.md context

Pi has no MCP and no built-in sub-agents. Its leverage is the entry-doc chain (`AGENTS.md` → memories → rules → skills). Front-load context there, not in chat. The cheaper the chat, the more turns you get per budget.

### Capability-package skills

Skills install on demand: `pi install @framework/<skill>`. The agent then references the skill by name. Skills declared in `AGENTS.md` are loaded for the session; uninstalled skills do not consume context.

### JSON mode for structured output

`pi --mode json` runs Pi in JSON-RPC mode over stdin/stdout — the agent's responses are structured tool calls. Use this when the harness integrates with the [orchestration daemon](./07-orchestration.md) or any other program that wants to parse Pi's output.

## Model selection strategy

Pick the model from the task's reversal cost — how expensive it is to undo a bad answer. See [Token efficiency](./05-token-efficiency.md) for the cost-multiplier table.

| Task class | Claude (Anthropic) | Codex (OpenAI) | Pi (default vendor) |
|------------|--------------------|----------------|---------------------|
| Triage / one-line classify | Haiku 4.5 | gpt-5-nano / o4-mini | model declared in SYSTEM.md (default cheap) |
| Refactor / edit | Sonnet 4.5 | gpt-5-codex | Sonnet 4.5 via OpenRouter or vendor key |
| Plan / architect | Opus 4.7 | gpt-5 / o5 | Opus 4.7 |
| Verify / scrutinize (different model than generator) | Sonnet 4.5 | gpt-5 | Sonnet 4.5 |
| Visual / UI judgement | Sonnet 4.5 (vision) | gpt-5 (vision) | Sonnet 4.5 (vision) |

The verify row exists because of the architectural rule: **the model that generated must not grade**. See `PROJECT-TEMPLATE-SPEC.md` §10.

## Prompt-refiner skills

When you find yourself rewriting the same kind of prompt repeatedly, promote it to a skill in `skills/prompt-refiners/<role>/`:

- `skills/prompt-refiners/scrutinizer/` — boilerplate for the QA verdict prompt
- `skills/prompt-refiners/operator/` — boilerplate for the terminal-state approval prompt
- `skills/prompt-refiners/parent-ai/` — boilerplate for cross-CLI escalation prompts

The agent invokes them by name; the bodies are versioned with the project. See [Skills discovery](./08-skills-discovery.md).
