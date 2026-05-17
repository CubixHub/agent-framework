# Rules & Conventions (Tri-Platform)

> Applies to: Claude Code, Codex, Pi. Rules are the enforceable layer of the memory model — they fire on edits, not at chat time. Rewrites Factory.ai's Rules & Conventions guide.

## Rules vs memory vs AGENTS.md vs skills

| Surface | When read | Enforced? | Scope |
|---------|-----------|-----------|-------|
| `AGENTS.md` | Session start | No | Session-wide context |
| `.agent-os/memories.md` | Session start | No | Project-wide context |
| `.agent-os/rules/*.md` | On edit (file-matched) | Yes (via post-edit hook) | Specific file globs |
| `skills/*/SKILL.md` | When invoked by name or detected | Yes (skill body runs) | A specific task class |

Rule of thumb:

- **AGENTS.md** = "where things live"
- **Memories** = "what we decided"
- **Rules** = "how we edit"
- **Skills** = "how we do a recurring task"

## Directory layout

```
.agent-os/rules/
├── _base/
│   ├── general.md        Universal rules (commits, secrets, push policy)
│   └── security.md       Lethal-trifecta, secret handling
├── frontend/
│   ├── typescript.md
│   └── css.md
├── backend/
│   ├── python.md
│   └── rust.md
└── testing/
    ├── vitest.md
    └── pytest.md
```

Categories are open — add `infra/`, `db/`, `api/` as needed. Keep each file one screen long.

## Rule format template

Every rule entry uses four fields. Keep entries atomic (one rule per entry).

```markdown
### <Rule name>

- **Applies to**: `<glob>` (e.g., `**/*.ts`, `packages/api/**`)
- **Rule**: <one sentence imperative>
- **Example**:
  ```ts
  // good
  ...
  // bad
  ...
  ```
- **Rationale**: <one sentence — the reason this rule exists>
```

The four fields are non-negotiable. Without **Applies to**, the post-edit hook can't route. Without **Rationale**, the rule will be re-litigated.

## Layered rules for teams

Personal preferences live at `~/.agent-os/rules/personal/`. Project rules at `.agent-os/rules/`. Project beats personal on conflict — the project repo is the source of truth.

Within a project, deeper paths override shallower ones for the same glob. E.g., `.agent-os/rules/frontend/typescript.md` overrides `_base/general.md` for `.ts` files. The post-edit hook merges by glob specificity.

## Glob-pattern workaround

Some CLIs (notably Pi) parse only literal extensions, not full globs, in their rule index. Workaround: keep one rule file per primary extension and use the rule body's **Applies to** field to narrow further. The post-edit hook respects the **Applies to** field at enforcement time even when the CLI's index does not.

## Auto-enforcement via hooks

The post-edit hook is the enforcement point. It reads the edited file's path, matches `.agent-os/rules/*.md` by **Applies to** glob, runs the lint/format step declared in the rule, and surfaces failures as `systemMessage`.

### Claude Code

`~/.claude/settings.json`:

```jsonc
{ "hooks": { "PostToolUse": [
  { "matcher": "Write|Edit|ApplyPatch",
    "command": "${PROJECT_DIR}/.agent-os/hooks/post-edit.sh" }
]}}
```

### Codex

`~/.codex/config.toml`:

```toml
[hooks]
post_tool_use = ".agent-os/hooks/post-edit.sh"
matchers = ["write", "edit", "apply_patch"]
```

### Pi

`~/.pi/SYSTEM.md` references the hook, plus install the `pi-hooks-bridge` capability package which bridges Pi's tool events to the same shell script.

Hook contract: read JSON `{"tool_input": {"file_path": "..."}}` from stdin; emit JSON `{"systemMessage": "..."}` or exit 0 silently. Never block the edit. The agent decides what to do with the surfaced feedback. See `skills/post-edit-hook/` for the reference implementation.
