# Implementation Backlog

## Done

- Create Python project metadata and dependency groups.
- Add Docker Compose services for app, PostgreSQL + pgvector, and Redis.
- Add pre-commit hooks for ruff and mypy.
- Add FastAPI app factory, health endpoint, and Prometheus metrics.
- Add SQLAlchemy setup and Alembic migration for sessions, messages, and memory fragments.
- Add Redis short-term memory interface with in-memory test double.
- Add long-term memory repository and semantic-search fallback for tests.
- Add memory router for STM + LTM context retrieval and consolidation.
- Add REST and WebSocket chat endpoints.
- Add tests for health, short-term memory, sessions, chat, and consolidation.
- Wire LangGraph agent graph into the actual chat flow.
- Fix auto-consolidation counting bug (was firing on every message).
- Fix InMemoryShortTermMemory class-level mutable defaults.
- Fix project name mismatch (conversational-agent → life-os).
- Add Notes system (model, schema, repository, service, API, tests).
- Add Reminders system (model, schema, repository, service, API, tests).
- Add natural language intent detection (regex + LLM-based).
- Add web chat UI (dark mode, session management, suggestions).
- Clean up 14+ empty stub files and unused directories.
- Update prompts, README, and .gitignore.

## Next

- Add Alembic migrations for notes and reminders tables.
- Add real LangSmith trace examples to docs.
- Add token counting and README token-reduction numbers.
- Add integration tests with testcontainers for Redis and PostgreSQL + pgvector.
- Add streaming token responses over WebSocket.
- Add CI for linting, tests, and coverage.
- Add fragment deduplication and confidence scoring.

## API Backlog

- Add pagination for history and memory fragments.
- Add API-key auth before deploying beyond local development.
- Add explicit `/end-session` command support in WebSocket.
- Add per-user memory export endpoint.
- Add per-user notes/reminders export endpoint.

## Operational Backlog

- Add production settings guidance.
- Add request IDs.
- Add structured request logging middleware.
- Add database backup guidance.
- Add dashboards for memory latency and LLM usage.
