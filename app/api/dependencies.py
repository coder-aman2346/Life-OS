from collections.abc import Callable
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.orm import Session

from app.agent.graph import build_graph
from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.memory.long_term import LongTermMemory
from app.memory.router import MemoryRouter
from app.memory.short_term import ShortTermMemory
from app.repositories.memory_repository import MemoryRepository
from app.repositories.note_repository import NoteRepository
from app.repositories.reminder_repository import ReminderRepository
from app.services.ai import ChatModelService, EmbeddingService, SummarizerService
from app.services.chat_service import ChatService
from app.services.intent_detector import IntentDetector
from app.services.note_service import NoteService
from app.services.reminder_service import ReminderService


@lru_cache
def get_redis_client() -> Redis:
    return Redis.from_url(get_settings().redis_url, decode_responses=True)


def get_short_term_factory(
    settings: Annotated[Settings, Depends(get_settings)],
    redis: Annotated[Redis, Depends(get_redis_client)],
) -> Callable[[str], ShortTermMemory]:
    def factory(session_id: str) -> ShortTermMemory:
        return ShortTermMemory(
            redis,
            session_id,
            ttl=settings.short_term_ttl_seconds,
            max_messages=settings.short_term_max_messages,
        )

    return factory


def get_long_term_memory(db: Annotated[Session, Depends(get_db)]) -> LongTermMemory:
    return LongTermMemory(MemoryRepository(db))


def get_embedding_service(settings: Annotated[Settings, Depends(get_settings)]) -> EmbeddingService:
    return EmbeddingService(settings)


def get_summarizer_service(
    settings: Annotated[Settings, Depends(get_settings)],
) -> SummarizerService:
    return SummarizerService(settings)


def get_chat_model_service(
    settings: Annotated[Settings, Depends(get_settings)],
) -> ChatModelService:
    return ChatModelService(settings)


def get_intent_detector(
    settings: Annotated[Settings, Depends(get_settings)],
) -> IntentDetector:
    return IntentDetector(settings)


def get_memory_router(
    short_term_factory: Annotated[
        Callable[[str], ShortTermMemory], Depends(get_short_term_factory)
    ],
    long_term: Annotated[LongTermMemory, Depends(get_long_term_memory)],
    embedder: Annotated[EmbeddingService, Depends(get_embedding_service)],
    summarizer: Annotated[SummarizerService, Depends(get_summarizer_service)],
) -> MemoryRouter:
    return MemoryRouter(
        short_term_factory=short_term_factory,
        long_term=long_term,
        embedder=embedder,
        summarizer=summarizer,
    )


# ── Notes & Reminders ─────────────────────────────────────────


def get_note_service(db: Annotated[Session, Depends(get_db)]) -> NoteService:
    return NoteService(NoteRepository(db))


def get_reminder_service(db: Annotated[Session, Depends(get_db)]) -> ReminderService:
    return ReminderService(ReminderRepository(db))


# ── Chat (wires everything together) ──────────────────────────


def get_chat_service(
    settings: Annotated[Settings, Depends(get_settings)],
    long_term: Annotated[LongTermMemory, Depends(get_long_term_memory)],
    memory_router: Annotated[MemoryRouter, Depends(get_memory_router)],
    chat_model: Annotated[ChatModelService, Depends(get_chat_model_service)],
    intent_detector: Annotated[IntentDetector, Depends(get_intent_detector)],
    note_service: Annotated[NoteService, Depends(get_note_service)],
    reminder_service: Annotated[ReminderService, Depends(get_reminder_service)],
) -> ChatService:
    agent_graph = build_graph(memory_router, chat_model)
    return ChatService(
        long_term=long_term,
        memory_router=memory_router,
        chat_model=chat_model,
        agent_graph=agent_graph,
        intent_detector=intent_detector,
        note_service=note_service,
        reminder_service=reminder_service,
        consolidation_turn_threshold=settings.consolidation_turn_threshold,
    )
