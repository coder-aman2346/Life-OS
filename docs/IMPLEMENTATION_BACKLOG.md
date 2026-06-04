# Implementation Backlog

## Current State

The repository currently contains the intended folder structure and placeholder Python files. There is no working FastAPI app, database configuration, dependency manifest, migration setup, worker setup, or test suite yet.

The next goal is to turn the scaffold into a runnable modular monolith.

## Build Order

### 1. Project Bootstrap

Tasks:

- Add `pyproject.toml` with FastAPI, SQLAlchemy, Alembic, Pydantic settings, Redis, Celery, pytest, and lint tooling.
- Add `.env.example`.
- Add `.gitignore` scoped to Python, local env files, caches, and IDE metadata.
- Replace empty `docker-compose.yml` with Postgres, Redis, API, and worker services.
- Add `README.md` with local setup.

Definition of done:

- Dependencies install cleanly.
- Local services can start.
- Basic test command exists.

### 2. FastAPI Foundation

Tasks:

- Implement `app/main.py`.
- Add `app/core/config.py`.
- Add `app/api/health.py`.
- Register API routers from a central router.
- Add application startup checks only where necessary.

Definition of done:

- `GET /health` returns a healthy response.
- App can run with `uvicorn app.main:app --reload`.

### 3. Database Foundation

Tasks:

- Add SQLAlchemy database engine/session setup.
- Add model base class.
- Implement models for users, tasks, reminders, notes, conversations, memories, and events.
- Configure Alembic.
- Generate initial migration.

Definition of done:

- Database tables can be created through migrations.
- Tests can use a separate database URL or local SQLite where practical.

### 4. Task Module

Tasks:

- Add task schemas.
- Add task repository.
- Add task service.
- Implement task API routes.
- Add tests for create, list, update, complete, and delete.

Definition of done:

- Task CRUD works through REST API.
- Status and due-date validation are covered.

### 5. Reminder Module

Tasks:

- Add reminder schemas.
- Add reminder repository.
- Add reminder service.
- Implement reminder API routes.
- Add timezone handling.
- Publish or record `ReminderCreated` events.

Definition of done:

- Reminder can be created for a concrete timestamp.
- Invalid past reminders are rejected or explicitly handled.

### 6. Scheduler and Notifications

Tasks:

- Configure Celery with Redis.
- Add a periodic job that finds due reminders.
- Mark triggered reminders safely.
- Add notification abstraction.
- Add Telegram notifier implementation.

Definition of done:

- Due reminders trigger exactly once.
- Notification failures are logged and retryable.

### 7. Notes Module

Tasks:

- Add note schemas.
- Add note repository.
- Add note service.
- Implement note API routes.
- Add basic tag support.

Definition of done:

- Notes can be created and retrieved by user.

### 8. Chat Service

Tasks:

- Define chat request and response schemas.
- Store incoming and outgoing messages.
- Build context from recent conversations and short-term memory.
- Route simple intents to task, reminder, note, memory, summary, or conversation handlers.
- Return a response with action metadata.

Definition of done:

- `POST /chat` can create tasks, reminders, and notes from plain messages.
- Pending task questions return real stored tasks.

### 9. Agent Layer

Tasks:

- Implement a planner interface.
- Start with rule-based classification.
- Add LLM-backed classification behind the same interface later.
- Add LangGraph workflow after tool contracts are stable.

Definition of done:

- Agent behavior is testable without Telegram.
- Tool execution is deterministic and auditable.

### 10. Memory Module

Tasks:

- Implement Redis short-term memory store.
- Implement PostgreSQL long-term memory service.
- Add memory extraction policy.
- Add memory retrieval by user.
- Add pgvector only after base memory works.

Definition of done:

- Recent messages are available for context.
- Durable user facts can be stored and recalled.

### 11. Telegram Integration

Tasks:

- Add Telegram webhook route.
- Verify Telegram secret token.
- Convert Telegram update to internal chat request.
- Send chat response back to Telegram.
- Store Telegram chat ID for notifications.

Definition of done:

- User can chat with the assistant through Telegram.

### 12. Summaries and Analytics

Tasks:

- Implement daily summary generation.
- Implement pending work summary.
- Implement weekly review.
- Add basic productivity analytics from tasks and reminders.

Definition of done:

- Summary responses are based on stored data, not generic text.

## First Sprint Recommendation

Build these first:

1. `pyproject.toml`
2. `docker-compose.yml`
3. `app/main.py`
4. `app/core/config.py`
5. `app/api/health.py`
6. Database base/session setup
7. `users` and `tasks` models
8. Task CRUD API
9. Minimal tests

Reason:

Task CRUD creates the first real vertical slice. It exercises API routing, validation, database access, services, repositories, tests, and Docker. Once this is stable, reminders, chat orchestration, and Telegram can reuse the same structure.

## Risk Register

### LLM Overuse

Risk:

The assistant becomes expensive and unreliable if every action depends on an LLM.

Mitigation:

Use deterministic parsing and service logic where possible. Use LLMs for ambiguous classification, summarization, and memory extraction.

### Memory Pollution

Risk:

The system stores too many low-value memories and recalls irrelevant facts.

Mitigation:

Use explicit memory types, importance scores, user scoping, and memory review/debug endpoints.

### Timezone Bugs

Risk:

Reminders fire at the wrong time.

Mitigation:

Store UTC timestamps, keep user timezone, and test date parsing around midnight and timezone boundaries.

### Premature Microservices

Risk:

Multiple deployable services slow development before product value exists.

Mitigation:

Use a modular monolith with clear boundaries. Split services later only when scaling or operational needs justify it.

### Integration Fragility

Risk:

Telegram, Gmail, Calendar, and WhatsApp APIs each add separate failure modes.

Mitigation:

Put integrations behind interfaces and keep internal chat/task/reminder flows independent.
