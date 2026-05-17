---
title: Linear Integration
type: integration
updated: 2026-05-17
---

# Linear Integration

The orchestration daemon uses Linear as a poll-claim-process state machine.
This doc gets you from "no Linear account" to "daemon claims my first issue".

## 1. Create a personal API key

1. Open https://linear.app/settings/api
2. Click **New API key**. Name it `orchestration-daemon`.
3. Copy the value (it shows once) into `integrations/linear/.env`:

```bash
cp integrations/linear/env.example integrations/linear/.env
$EDITOR integrations/linear/.env
```

Note: the template file is `env.example` (no leading dot) because the
workspace ACL blocks writes to `.env*` paths. Rename to `.env` after
copying.

The daemon reads these via the standard environment — `source .env` before
launching or wire it through your tmux/systemd unit.

## 2. Pick a team

Linear groups issues by team. The daemon scopes everything to one team key.

- Find your team key in Linear UI (e.g., `AEV`, `ENG`, `OPS`).
- Set `LINEAR_TEAM_KEY=<key>` in `.env`.
- Optionally pin `LINEAR_PROJECT_ID=<uuid>` to filter to a single project.

## 3. State machine setup

Run `bash integrations/linear/bootstrap.sh` to create the canonical 8 states
the daemon expects:

| State | Daemon eligibility | Owner |
|---|---|---|
| Triage | no | operator |
| Agent Queue | YES (daemon polls) | daemon |
| Processing | no (in-flight) | daemon |
| Evaluating | no | operator |
| Parent AI Review | YES (forces parent-ai routing) | daemon |
| Human Approval | no (terminal) | operator |
| Completed | no (terminal) | operator |
| Failed | no (terminal) | daemon (after 3 retries) |

The script is idempotent; it creates missing states only.

## 4. Label taxonomy

The daemon's H3 routing reads labels of the form `@<role>`. Recommended
canonical labels (the bootstrap creates them all):

| Prefix | Examples | Purpose |
|---|---|---|
| `@<role>` | `@parent-ai`, `@scrutinizer`, `@code-architect` | Agent routing |
| `type:*` | `type:feature`, `type:bug`, `type:tech-debt` | Work classification |
| `prio:*` | `prio:P0`, `prio:P1`, `prio:P2`, `prio:P3` | Priority |
| `phase:*` | `phase:0`, `phase:1` | Phase ramp |
| `gate:*` | `gate:proxy-pass`, `gate:phase-1-exit` | Acceptance gates |

Only `@<role>` is load-bearing for routing; the rest are advisory metadata.

## 5. Issue body format

The daemon parses an `Acceptance:` block out of the body — see the
`parse_acceptance()` regex in `orchestration/runner.py`. Recommended template:

```
Phase: <number + name>
Deliverables:
- <concrete artifact>
Acceptance:
- <observable pass/fail criterion>
- <observable pass/fail criterion>
Effort: ~N dev-days
Risk: <one-line note + mitigation>
```

## 6. Verdict comment format

Every subagent posts this block as its terminal stdout. The daemon parses
the `VERDICT:` line and posts the whole comment to the issue before
transitioning state.

```
VERDICT: PASS | PROXY_PASS | FAIL | NEEDS_HUMAN | CONTINUE | HUMAN_APPROVAL_REQUIRED
Artifacts: <comma-separated paths or URLs>
Summary: <1-3 sentences>
Gate ref: <test plan section, e.g. "§2.1 Spike 0.1">
```

## 7. Launch the daemon

```bash
source integrations/linear/.env
cp orchestration/WORKFLOW.md.tmpl orchestration/WORKFLOW.md
# edit pm_provider: linear (default) and agent_role_routing as needed
bash orchestration/scripts/start.sh
tail -f /tmp/orchestration-daemon-master.log
```

## 8. Troubleshooting

| Symptom | Fix |
|---|---|
| `linear team X not found` | Confirm `LINEAR_TEAM_KEY` matches the UI exactly |
| `state X not found` | `rm /tmp/linear_state.json` to force schema refresh |
| Claim races | Linear's state transition is atomic enough; if two daemons run, only one wins |
| Rate limit | Linear allows ~60 req/min/key; 30s poll fits comfortably |

For the schema-cache file (`/tmp/linear_state.json`), see
`orchestration/pm_adapters/linear_adapter.py`.
