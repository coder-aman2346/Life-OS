# Conversational Agent Project Plan

## Product Direction

Build an open-source, portfolio-grade conversational agent that demonstrates persistent memory across sessions. The goal is not only to chat, but to show production judgment: clear memory boundaries, durable storage, semantic retrieval, observability, tests, and a crisp demo script.

## Target Architecture

- FastAPI for REST and WebSocket entry points.
- LangGraph for explicit agent state transitions.
- Redis lists with TTL for short-term memory.
- PostgreSQL for sessions, messages, and long-term memory fragments.
- pgvector for semantic memory retrieval.
- GPT-4o-mini for summarization and default chat.
- `text-embedding-3-small` for embeddings.
- Prometheus metrics, JSON logs, and LangSmith trace hooks.

## Milestones

1. Scaffold repo, dependencies, Docker, env docs, and pre-commit hooks.
2. Implement Redis short-term memory with LPUSH/LRANGE, TTL, and max-turn caps.
3. Implement PostgreSQL long-term memory schema with pgvector.
4. Build the memory router that merges recent context and semantic fragments.
5. Wire the LangGraph retrieve → call LLM → update memory graph.
6. Expose FastAPI session, chat, history, memory, forget, and WebSocket endpoints.
7. Measure TOON-style context compression against raw JSON history.
8. Add observability and integration tests.
9. Record the demo: tell the agent facts, consolidate, return in a new session, show memory.
