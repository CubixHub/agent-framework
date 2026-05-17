# Seven layers — per-language commands

## Layer 1 — Static
| Language   | Command |
|---|---|
| TypeScript | `npm run lint && npm run typecheck && prettier --check .` |
| Python     | `ruff check . && mypy --strict . && ruff format --check .` |
| Rust       | `cargo clippy -- -D warnings && cargo fmt --check` |
| Go         | `golangci-lint run && gofmt -l . | wc -l` |

## Layer 2 — Unit + property
| Language   | Command |
|---|---|
| TypeScript | `vitest run` (with `fast-check` for properties) |
| Python     | `pytest -x --hypothesis-show-statistics` |
| Rust       | `cargo test --lib` (with `proptest` crate) |
| Go         | `go test ./...` (with `testing/quick`) |

## Layer 3 — Integration
- Run against a real DB / queue / service (no internal mocks).
- Use `testcontainers` (TS, Py, Java) or `dockertest` (Go).
- MSW (TS) or `responses` (Py) only at the external-API boundary.

## Layer 4 — End-to-end user-flow
- Playwright / Cypress (web).
- Detox (React Native).
- XCTest UI / Espresso (native mobile).
- **Mandatory**: assert UI text AND server-state for every flow.

## Layer 5 — Behavioural fingerprinting
- Track distributional metrics over time (latency p50/p95/p99, error rate, output
  embedding distribution for ML).
- Tool: opentelemetry traces + a metrics store (Prometheus, Datadog).
- Alarm threshold: 2σ drift over rolling 100-run window.

## Layer 6 — Mutation testing
| Language   | Tool |
|---|---|
| TypeScript | `stryker` |
| Python     | `mutmut` or `cosmic-ray` |
| Rust       | `cargo-mutants` |
| Go         | `go-mutesting` |

Target ≥60% mutation survival (most mutants killed by tests).

## Layer 7 — Trace audit
- Log every tool call the agent makes (args + result hash).
- Diff claimed actions ("I edited X") vs `git diff --stat`.
- If they don't match, the agent is lying or hallucinating — escalate.
