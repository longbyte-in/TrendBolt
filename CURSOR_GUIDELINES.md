## Cursor Engineering Guidelines

These guidelines standardize how we build and review code in TrendBolt using Cursor. They focus on testability, clarity, maintainability, and compliance with MCP and Python best practices.

### 1) Unit tests
- Prefer `pytest` with clear Arrange–Act–Assert sections.
- Place tests under `tests/` mirroring package structure; name files `test_*.py`.
- Target coverage ≥ 80% for core modules; add regression tests for bugs.
- No live network calls in unit tests. Use fakes/mocks, `responses`/`respx`, or VCR for HTTP.
- Test edge cases, error paths, and idempotency (especially MCP tools).
- Use fixtures for setup; keep fixtures small and explicit.

### 2) Naming
- Use descriptive, intention-revealing names: functions as verbs, classes as nouns.
- Avoid abbreviations; prefer whole words. Booleans start with `is_`, `has_`, `should_`.
- Constants in `UPPER_SNAKE_CASE`; modules and packages in `lower_snake_case`.
- Choose names that encode domain meaning over implementation details.

### 3) SOLID principles
- Single Responsibility: each module/class/function does one thing well.
- Open/Closed: extend behavior via composition or small strategies; avoid modifying stable code.
- Liskov Substitution: types and protocols should be safely swappable.
- Interface Segregation: keep interfaces small; accept protocols or callables over broad types.
- Dependency Inversion: depend on abstractions, not concrete implementations.

### 4) KISS principle
- Prefer the simplest design that works; avoid premature optimization.
- Keep functions small (screenful max), with early returns and minimal branching.
- Favor composition over deep inheritance and over-generalized frameworks.

### 5) Readability & maintainability
- Follow PEP 8 and use type hints consistently; enable `mypy` where practical.
- Write docstrings (PEP 257) for public functions/classes describing purpose and contracts.
- Handle errors explicitly; no bare `except`. Log context, not secrets.
- Avoid deep nesting; extract guard clauses and helper functions.
- Write deterministic, side-effect-light functions where possible.

### 6) MCP standards
- Build tools that are small, idempotent, and validate inputs/outputs (JSON schema via `pydantic`).
- Use clear tool names and stable contracts; version tools when breaking changes are needed.
- Ensure tools handle timeouts, retries, and rate limits gracefully.
- Document each tool: purpose, inputs, outputs, failure modes, and examples.
- Test via an MCP-compatible client and the MCP Inspector prior to release.
- Reference: Model Context Protocol overview: [modelcontextprotocol.io/docs/getting-started/intro](https://modelcontextprotocol.io/docs/getting-started/intro)

### 7) Python best practices
- Use `pyproject.toml` (or `requirements.txt`) with pinned versions; maintain a reproducible venv.
- Run linters/formatters: `ruff`/`flake8`, `black`, `mypy` in CI.
- Prefer `httpx` (async) with timeouts and retries (`tenacity`) for external calls.
- Guard secrets via environment variables; never commit credentials; redact logs.
- Structure code with clear boundaries: config, models (Pydantic), tools/clients, services.

### 8) PR checklist (quick)
- [ ] Tests added/updated and passing; no live network in unit tests
- [ ] Types/linters clean; no new warnings
- [ ] Function/class names and docstrings are clear
- [ ] Errors handled; retries/backoff where needed
- [ ] Public contracts (MCP tools) documented and remain backward compatible or versioned

### 9) Documentation
- Keep `README.md` user-focused (setup/run). Keep `DESIGN.md` architecture-focused and current.
- When adding new tools or endpoints, include minimal examples and env var notes.


