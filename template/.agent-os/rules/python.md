# Python rules

- PEP 8 with type hints on every function signature and module-level attribute.
- `src/` layout: `src/<pkg>/__init__.py`, tests under `tests/` mirroring the package.
- `ruff` for lint + format; `mypy --strict` for type-check.
- Use `dataclass(slots=True, frozen=True)` for value objects at boundaries.
- `Protocol` for interfaces; never use ABCs unless you need MRO.
- Errors: raise the most specific exception class; never bare `except:`. Wrap
  external failures in domain exceptions.
- Async: `asyncio` only; never mix with threads except via `asyncio.to_thread`.
- Config via `pydantic-settings`; never `os.environ` access scattered.
- Use `pathlib.Path` for paths; never string concatenation.
- `pytest` with `pytest-asyncio` for async; coverage gate at 80%+.
- Logging: `structlog` with JSON output in prod, console in dev.
- No globals, no module-level side effects, no `from x import *`.
