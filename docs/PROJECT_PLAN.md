# Life OS Project Plan

## Product Goal

Life OS is a personal chief-of-staff assistant that accepts natural-language messages, turns them into structured actions, remembers useful user context, and proactively follows up through notifications.

The first production-quality goal is not a fully autonomous multi-agent system. The first goal is a reliable assistant that can:

- Receive a message from API or Telegram.
- Understand whether the user wants a task, reminder, note, summary, or normal conversation.
- Create, list, update, and complete tasks.
- Create reminders and trigger notifications at the right time.
- Store short-term conversation context.
- Store important long-term memories.
- Produce useful daily and weekly summaries from stored data.

## V1 Scope

V1 should prove the core loop:

User message -> intent detection -> tool execution -> persistence -> response -> notification when needed

Included:

- FastAPI backend.
- PostgreSQL database.
- Redis for short-term memory and background jobs.
- Telegram bot integration as the primary UI.
- Tasks, reminders, notes, conversations, and memories.
- Basic agent workflow with deterministic routing first.
- Scheduler worker for reminders.
- Docker Compose for local development.
- Tests for services and API routes.

Excluded from V1:

- WhatsApp.
- Android companion app.
- Gmail and Google Calendar write access.
- Full autonomous planning.
- Kafka.
- Complex multi-service deployment.

These should wait until the core loop is stable.

## Architecture Direction

Keep the repository as a modular monolith for V1. The folder names can represent logical services, but deploying multiple physical services too early will slow development and testing.

Recommended runtime components:

- `api`: FastAPI app serving REST routes and Telegram webhook.
- `worker`: Celery worker processing reminders and background jobs.
- `postgres`: durable relational storage.
- `redis`: short-term memory, cache, and Celery broker.

Recommended logical modules:

- `app/api`: HTTP route layer.
- `app/services`: business logic.
- `app/agents`: planner, intent router, and tool execution graph.
- `app/memory`: short-term, long-term, and semantic memory.
- `app/scheduler`: reminder scheduling and background jobs.
- `app/integrations`: Telegram and future external APIs.
- `app/db`: models, repositories, migrations, and database session setup.

## Agent Strategy

Start with a deterministic planner before introducing complex LangGraph behavior.

Phase 1 routing:

- `task`: create, list, update, complete, delete tasks.
- `reminder`: create scheduled reminder.
- `note`: save or retrieve notes.
- `memory`: store or recall user preferences/facts.
- `summary`: summarize today's work or pending work.
- `conversation`: answer without tool execution.

Phase 2 routing:

- Replace simple routing with a LangGraph workflow.
- Add planner node, tool nodes, memory node, and response node.
- Add confidence scores and fallback clarification.

Do not make every request an LLM call if a deterministic parser is enough. Reliability matters more than novelty.

## Memory Strategy

Memory should be explicit and inspectable.

Short-term memory:

- Store recent messages in Redis.
- Key pattern: `short_memory:{user_id}:{session_id}`.
- TTL: 24 hours.
- Purpose: conversation continuity.

Long-term memory:

- Store durable user facts in PostgreSQL.
- Example: "User prefers coding at night."
- Each memory should have type, importance, source conversation, and timestamps.

Semantic memory:

- Use pgvector after the base memory table is working.
- Generate embeddings only for memories worth recalling.
- Search should always be scoped by `user_id`.

## Data Model

Core tables:

- `users`
- `tasks`
- `reminders`
- `notes`
- `conversations`
- `memories`
- `memory_embeddings`
- `events`

Important design rules:

- Every user-owned table must include `user_id`.
- Store timestamps in UTC.
- Keep the user's timezone on the `users` table.
- Use status enums for tasks and reminders.
- Do not delete user data by default; prefer soft delete where useful.

## API Surface

Minimum V1 API:

- `POST /chat`
- `POST /telegram/webhook`
- `POST /tasks`
- `GET /tasks`
- `PATCH /tasks/{task_id}`
- `DELETE /tasks/{task_id}`
- `POST /reminders`
- `GET /reminders`
- `POST /notes`
- `GET /notes`
- `GET /health`

The `/chat` endpoint should become the main orchestration entry point. CRUD APIs are still useful for tests, future UI, and debugging.

## Events

Use an `events` table first. Add Redis Streams later only when multiple workers or integrations need event fan-out.

Initial events:

- `TaskCreated`
- `TaskCompleted`
- `ReminderCreated`
- `ReminderTriggered`
- `NoteCreated`
- `MemoryStored`
- `DailySummaryGenerated`

This keeps the architecture interview-friendly without adding operational complexity too early.

## Milestones

### Milestone 1: Backend Foundation

- FastAPI app boots locally.
- Health endpoint works.
- Database session configured.
- SQLAlchemy models created.
- Alembic migrations configured.
- Docker Compose starts API, Postgres, Redis.

Success criteria:

- `docker compose up` starts local dependencies.
- `pytest` runs.
- `/health` returns success.

### Milestone 2: Tasks, Notes, Reminders

- CRUD APIs implemented.
- Service and repository layers added.
- Reminder records can be created with timezone-aware trigger times.
- Basic tests cover happy paths and validation.

Success criteria:

- User can create and list tasks, notes, and reminders through REST APIs.

### Milestone 3: Chat Orchestration

- `POST /chat` accepts natural-language messages.
- Planner maps messages to tool actions.
- Tool execution creates tasks/reminders/notes.
- Conversation history is stored.
- Basic response generation works.

Success criteria:

- "Remind me to pay electricity bill on 10th at 9 AM" creates a reminder.
- "Add finish resume as a task for tomorrow" creates a task.
- "What tasks are pending?" lists open tasks.

### Milestone 4: Telegram UI

- Telegram webhook receives messages.
- Messages flow through the same chat service.
- Bot replies with the generated response.
- Reminder notifications are sent through Telegram.

Success criteria:

- Telegram becomes usable as the primary interface.

### Milestone 5: Memory

- Redis short-term memory stores recent conversation context.
- PostgreSQL long-term memory stores durable facts.
- Memory extraction runs after chat messages.
- Basic memory retrieval improves responses.

Success criteria:

- Assistant remembers stable preferences and can use them later.

### Milestone 6: Summaries and Analytics

- Daily summary endpoint/job.
- Weekly review generation.
- Time/task analytics from stored task and conversation data.

Success criteria:

- "Summarize today's work" returns a useful summary based on actual stored records.

## Engineering Standards

- Add tests with each feature.
- Keep business logic out of route handlers.
- Use repositories for database access.
- Use Pydantic schemas for request and response contracts.
- Keep integrations behind interfaces so Telegram can be replaced or expanded.
- Use environment variables for secrets.
- Document setup commands in `README.md`.
- Prefer simple, observable flows before distributed architecture.

## Portfolio Positioning

This project should demonstrate:

- Backend API design.
- Database modeling.
- Background jobs.
- Event-driven thinking.
- AI agent orchestration.
- Memory architecture.
- Real-world integrations.
- Dockerized local development.
- Testing and production readiness.

The strongest resume version is not the broadest version. It is the version where the core workflows work reliably end to end.
