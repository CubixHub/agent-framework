# PM Tool Choice — Linear vs Plane

> Applies to: any Framework project with the [orchestration daemon](./07-orchestration.md). The PM tool is the source of truth for ticket state; the daemon adapter abstracts the difference but the choice still matters.

## TL;DR

- **Startup, SaaS, small team, fastest path** → **Linear**.
- **Self-hosted, regulated, enterprise, custom workflows** → **Plane**.

## Feature comparison

| Dimension | Linear | Plane |
|-----------|--------|-------|
| **Hosting** | SaaS only (US/EU regions) | Self-host (Docker, k8s, bare metal) or SaaS |
| **State machine flexibility** | Fixed core states (Triage / Backlog / Todo / In Progress / Done / Canceled) + custom "workflow states" per team | Fully customizable states per workspace |
| **Label taxonomy** | Labels + parent-child labels; team-scoped | Labels + label groups; workspace-scoped |
| **API** | GraphQL (single endpoint); excellent docs; mature client libs | REST (`/api/v1/`); under heavier evolution; usable |
| **Rate limits** | 1500 req/hour per token (generous) | Configurable per deployment; SaaS default 600/hour |
| **Webhooks** | Reliable, signed payloads, retry semantics | Available; signature verification improving in 2026 |
| **Multi-workspace** | Yes (org → teams → projects → issues) | Yes (instance → workspace → project → issue) |
| **Pricing** | Per-seat SaaS; free tier limited; Standard ~$8–$10/user/mo (verify on linear.app) | Open-source / community free; cloud and enterprise tiers from Plane.so (verify on plane.so) |
| **Agent-friendliness** (claim/comment/transition patterns) | Native fit — short cycle times, mutation-heavy GraphQL, fast state changes | Workable — REST cycle adds a few ms; field coverage strong |
| **Customer trajectory** | Mature; high adoption among small/mid YC-style teams | Growing; preferred where data residency or self-host matters |
| **Lock-in risk** | Vendor lock-in via custom workflows + API | Lower (open source); migrating between deployments straightforward |
| **Data residency** | Vendor-controlled regions | Operator-controlled |

## Decision matrix

| If your project is… | Recommend |
|---------------------|-----------|
| A startup shipping fast; team < 50 | Linear |
| An enterprise with compliance constraints | Plane (self-hosted) |
| Open-source / public; want contributors to see tickets without sign-up | Plane (community instance) |
| Has existing Linear workspaces in the org | Linear (don't fragment) |
| Has existing Plane self-host | Plane (don't fragment) |
| Needs fully custom states (e.g., regulated medical workflow) | Plane |
| Optimizes for daemon poll latency at scale | Linear (GraphQL + better rate limits at scale) |
| Operator wants the daemon to "just work" with minimal config | Linear |

## How `init-project.sh` prompts the choice

When provisioning a new project (`init-project.sh` or `/connx init` if ConnX is the harness), the script asks:

```
Which PM tool? [1] Linear (SaaS, fastest path) [2] Plane (self-host, customizable)
```

The answer writes `.agent-os/orchestration.yaml`:

```yaml
pm_tool: linear            # or: plane
pm_workspace: <id>
pm_api_token_env: LINEAR_API_KEY   # or: PLANE_API_KEY
pm_base_url: https://api.linear.app/graphql   # or: https://<plane-host>/api/v1
```

And copies the right adapter from `integrations/{linear,plane}/`. Switching later is supported but requires re-running the init script with `--reconfigure` — the adapter changes and a small ADR is required to track the migration.

## Workflow conventions both adapters require

Regardless of choice, the project must expose these states to the daemon. The adapter maps the local PM names to these canonical ones:

```
Triage  →  Agent Queue  →  Processing  →  Evaluating
            →  Parent AI Review  →  Human Approval  →  Completed
                                                    ↘  Failed
```

For Linear: configure as a custom workflow on the daemon's team. Set the Agent Queue state to `started` lifecycle so claim/in-progress semantics work.

For Plane: configure as workspace states. Set Agent Queue to `started` group; Completed/Failed to `completed`/`cancelled` groups respectively.

The daemon's adapter validates the workflow on startup and refuses to run if any required state is missing — the fatal-startup-error pattern (PROJECT-TEMPLATE-SPEC §8).

## Labels both adapters use

- `agent:claude` / `agent:codex` / `agent:pi` — pin a ticket to a specific worker CLI (otherwise daemon uses default)
- `verdict:proxy-pass` — set automatically when a worker returns `PROXY_PASS`
- `proxy-debt` — set on follow-up tickets created by a `PROXY_PASS`
- `requires-operator` — pin to Human Approval; daemon will not auto-route past

## Cross-references

- `integrations/linear/README.md` and `integrations/plane/README.md` — adapter implementations
- [Orchestration](./07-orchestration.md) — the daemon that consumes the adapter
- [Autonomy modes](./10-autonomy-modes.md) — operator-owned terminal-state invariant
