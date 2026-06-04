# Life OS

Life OS is a personal chief-of-staff assistant. It will accept natural-language messages, convert them into structured actions, remember useful context, and proactively follow up through reminders and summaries.

## Current Goal

Build a reliable V1 modular monolith:

- FastAPI backend.
- PostgreSQL for durable data.
- Redis for short-term memory and background jobs.
- Celery worker for reminders.
- Telegram as the first real user interface.
- Tasks, reminders, notes, conversations, and memory.

The first vertical slice should be task CRUD because it validates the API, database, service, repository, schema, Docker, and test structure.

## Planning Docs

- [Project Plan](docs/PROJECT_PLAN.md)
- [Implementation Backlog](docs/IMPLEMENTATION_BACKLOG.md)

## Recommended Build Sequence

1. Bootstrap Python dependencies and local Docker services.
2. Implement FastAPI health endpoint.
3. Add database setup and migrations.
4. Build task CRUD.
5. Add reminders and scheduler.
6. Add chat orchestration.
7. Add Telegram integration.
8. Add memory and summaries.

## Architecture Principle

Keep V1 as a modular monolith. The code should have clear service boundaries, but the deployment should stay simple until the core user workflows are reliable end to end.
