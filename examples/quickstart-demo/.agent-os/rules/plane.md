# Plane rules

Plane (https://plane.so) is self-hostable and uses workspaces → projects → issues.
Same agent contract as Linear; different API shape.

## Issue body format
Identical to Linear (`linear.md`). The state-machine and verdict-comment formats
are the same.

## Plane-specific differences
- States are per-project, configurable: create `Triage`, `Agent Queue`, `Processing`,
  `Evaluating`, `Parent AI Review`, `Human Approval`, `Completed`, `Failed`.
  Use `integrations/plane/bootstrap.sh` to create them automatically.
- Labels are per-workspace; create role labels (`@implementer`, `@scrutinizer`, etc.)
  in workspace settings.
- Modules ≈ Linear projects. Cycles ≈ Linear cycles.

## API auth
- Personal access token in `.env` as `PLANE_API_KEY`.
- Workspace slug as `PLANE_WORKSPACE_SLUG`.
- Project ID as `PLANE_PROJECT_ID`.
- Base URL as `PLANE_API_BASE_URL` (defaults to https://api.plane.so).

## State transitions
Use `pm_adapters/plane_adapter.py` from the orchestration daemon. Never patch
Linear-style mutations into Plane — endpoints differ.
