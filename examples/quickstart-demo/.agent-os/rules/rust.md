# Rust rules

- `clippy -- -D warnings` enforced. `cargo fmt` on every save.
- `no_std` where possible (libraries); `std` only for binaries and integration crates.
- Idiomatic `Result<T, E>` for recoverable errors; `panic!` only on impossible states.
- `thiserror` for library error types; `anyhow` for application code.
- `tokio` for async runtime (full-featured) or `smol` for low-dep.
- `serde` with `#[serde(deny_unknown_fields)]` on every deserialized type.
- FFI: minimum surface area, document `# Safety` on every `unsafe fn`, exhaustive tests.
- Concurrency: prefer `Arc<Mutex<T>>` only when necessary; `tokio::sync::mpsc` for
  channels. Document Send/Sync bounds on public types.
- Tests live in `tests/` (integration) and `#[cfg(test)] mod tests {}` (unit).
- Benchmarks via `criterion`. Profiling via `flamegraph` or `samply`.
- Forbid `unwrap()` and `expect()` in production code (allow in tests).
