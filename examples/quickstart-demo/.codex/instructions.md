# Codex instructions for quickstart-demo

> Codex reads `AGENTS.md` (canonical, all 3 CLIs) and `CODEX.md` (this CLI's overlay).
> Per-project conventions, rules, and skills live under `.agent-os/` — shared with
> Claude Code and Pi.

## When invoked
1. Read `../AGENTS.md` for project context.
2. Read `../.agent-os/rules/` for coding conventions matching the file you'll edit.
3. Invoke `skill-discovery` BEFORE any other tool call. Skills live at
   `../.agent-os/skills/`. If no skill matches the task, invoke `skill-creator`.
4. Honor the verification-first principle: no work is "done" until verification PASSes.

## Allowed operations
- File ops within the project tree.
- Shell commands with sandbox-policy as configured.
- Reading the wiki — write back findings via the `wiki-curator` skill.

## Forbidden
- `git push --force` without explicit ask.
- `git commit --no-verify`.
- Modifying `wiki/raw/`.
- Writing secrets to source files.

## PM tool: none
See `../.agent-os/rules/none.md` for the issue/verdict-comment format.

## Stack: typescript python
Apply the matching `.agent-os/rules/<language>.md` file.
