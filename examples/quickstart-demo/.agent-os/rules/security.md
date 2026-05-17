# Security rules

## Secrets
- Never hardcode. `.env*` is gitignored; commit only `.env.example`.
- Validate required env vars at startup; fail-fast if missing.
- Rotate keys when an agent or contributor leaves the project.

## Input validation
- Validate all external input with Zod (TS) / Pydantic (Py) at the boundary.
- Treat anything from the network, filesystem, or another process as untrusted.

## Lethal trifecta
A request becomes dangerous when these three converge in one execution path:
1. Untrusted input (user prompts, file contents, web responses)
2. Sensitive data access (DB rows, secrets, customer data)
3. Exfiltration path (network egress, log write to shared sink)

Break ONE of these three; documented in `wiki/plan/security.md`.

## Errors
- Log detailed errors server-side (with PII redacted). Return generic messages to clients.
- Never return stack traces, file paths, SQL fragments, or internal IDs to clients.

## Auth
- Check auth on every protected route via middleware/guard. Never trust client claims.
- Refresh tokens never live in localStorage; httpOnly cookies or memory only.

## Dependencies
- `npm audit` / `cargo audit` / `pip-audit` on every CI run. Fail on high+.
- Pin versions in lockfiles. Renovate/Dependabot for upgrades.

## Agent-runtime specifics
- Never let an agent install new shell binaries without explicit human ack.
- Hook scripts must run offline (no network).
- Sandbox external code execution (Docker, microVM, or vendor-provided sandbox).
