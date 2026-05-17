# Changelog

All notable changes to this Framework are recorded here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows
[SemVer](https://semver.org/).

## [Unreleased]

## [0.1.0] — 2026-05-17

### Added

- Initial release.
- `template/` scaffold for tri-CLI agent-native projects: `AGENTS.md` as
  canonical entry doc; `CLAUDE.md`, `CODEX.md`, `PI.md`, `SYSTEM.md` as
  CLI-specific overlays.
- `.agent-os/` shared runtime config: `settings.json`, `memories.md`, nine
  rule files (general / typescript / python / rust / api / testing / security /
  wiki / linear + plane), five hooks (post-edit, wiki-lint, format-on-edit,
  memory-capture, pre-commit).
- `.claude/`, `.codex/`, `.pi/` CLI overlays with cross-references to
  `.agent-os/`.
- `wiki/` Karpathy LLM-wiki scaffold: `SCHEMA.md`, `index.md`, `log.md`,
  `PLAN.md`, `IDEAS.md`, `STATUS.md`, plus `plan/` (verification-strategy,
  security, reuse-map, packages master docs, ADR template).
- `scripts/init-project.sh` — interactive scaffolder with PM-tool and
  CLI-selection sub-scripts (`select-pm.sh`, `select-cli.sh`),
  `verify-install.sh`, `install-prereqs.sh`, `skill-pull.sh`.
- `README.md`, `INSTALL.md` root entry docs.
- `examples/README.md` stub catalog.

### Known limitations

- `install-prereqs.sh` supports macOS / Debian / Ubuntu only; other Linux
  distros fall back to manual instructions.
- The orchestration daemon, sibling skills/agents/integrations, and full power-
  user docs are owned by sibling components and are intentionally out of scope
  for this changelog entry.

[Unreleased]: about:blank
[0.1.0]: about:blank

<!-- END -->
