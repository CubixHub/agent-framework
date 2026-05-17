---
title: Plane Integration
type: integration
updated: 2026-05-17
---

# Plane Integration

The orchestration daemon can use [Plane.so](https://plane.so) as its PM
state machine in place of Linear. Same Issue shape, same verdict
routing, different REST endpoints.

## 1. Create an API key

Hosted Plane: https://app.plane.so → workspace **Settings → API tokens**.
Self-hosted: same path under your installation's settings.

Copy the value into `integrations/plane/env.example` (renamed to `.env`):

```bash
cp integrations/plane/env.example integrations/plane/.env
$EDITOR integrations/plane/.env
```

## 2. Identify workspace + project

Plane URLs look like `https://app.plane.so/<workspace-slug>/projects/<uuid>/`.

- `PLANE_WORKSPACE_SLUG` — the slug after `app.plane.so/`.
- `PLANE_PROJECT_ID` — the project UUID from the URL.
- `PLANE_API_BASE_URL` — defaults to `https://api.plane.so/api/v1`;
  override for self-hosted (e.g. `https://plane.example.com/api/v1`).

## 3. State machine setup

Run `bash integrations/plane/bootstrap.sh` to create the canonical 8
workflow states. Plane state groups map roughly to Linear's:

| State | Plane group | Daemon eligibility | Owner |
|---|---|---|---|
| Triage | `backlog` | no | operator |
| Agent Queue | `unstarted` | YES (daemon polls) | daemon |
| Processing | `started` | no (in-flight) | daemon |
| Evaluating | `started` | no | operator |
| Parent AI Review | `started` | YES (forces parent-ai) | daemon |
| Human Approval | `started` | no (terminal) | operator |
| Completed | `completed` | no (terminal) | operator |
| Failed | `cancelled` | no (terminal) | daemon (after 3 retries) |

## 4. Label taxonomy

Same as Linear: `@<role>`, `type:*`, `prio:*`, `phase:*`, `gate:*`.
Only `@<role>` is load-bearing for routing.

The bootstrap script creates the canonical label set.

## 5. Issue body format

Plane stores descriptions as both HTML (`description_html`) and
stripped text (`description_stripped`). The adapter prefers
`description_stripped`. Use the same `Acceptance:` block convention
as Linear; the regex in `orchestration/runner.py` parses both backends.

## 6. Verdict comment format

Identical to Linear:

```
VERDICT: <one of the seven>
Artifacts: <paths|urls>
Summary: <1-3 sentences>
Gate ref: <test plan section>
```

## 7. Launch

```bash
source integrations/plane/.env
cp orchestration/WORKFLOW.md.tmpl orchestration/WORKFLOW.md
# in WORKFLOW.md set: pm_provider: plane
bash orchestration/scripts/start.sh
tail -f /tmp/orchestration-daemon-master.log
```

## 8. Endpoint reference

| Operation | Method + path |
|---|---|
| List issues | `GET /workspaces/{slug}/projects/{id}/issues/?state=<csv>&per_page=100` |
| Update issue state | `PATCH /workspaces/{slug}/projects/{id}/issues/{issue_id}/` body: `{"state": "<sid>"}` |
| Add comment | `POST /workspaces/{slug}/projects/{id}/issues/{issue_id}/comments/` body: `{"comment_stripped": "..."}` |
| List states | `GET /workspaces/{slug}/projects/{id}/states/` |
| List labels | `GET /workspaces/{slug}/projects/{id}/labels/` |

Auth header: `X-API-Key: <token>` (NOT `Authorization: Bearer ...`).

## 9. Troubleshooting

| Symptom | Fix |
|---|---|
| `plane state X not found` | `rm /tmp/plane_state.json` to force schema refresh |
| HTTP 401 | Confirm `X-API-Key` and that the token has not been revoked |
| HTTP 404 on `/issues/` | Confirm `PLANE_WORKSPACE_SLUG` is the slug, not the display name |
| `description` empty | Plane stores rich-text; the adapter reads `description_stripped` then falls back to `description`. Edit the issue to trigger stripped-text generation if needed |

Adapter source: `orchestration/pm_adapters/plane_adapter.py`.
Plane API reference: https://developers.plane.so/api-reference/introduction
