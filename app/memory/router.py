from collections.abc import Callable

from app.memory.long_term import LongTermMemory
from app.memory.short_term import ShortTermMemoryProtocol
from app.schemas.memory import MemoryContext, MemoryFragmentRead
from app.services.ai import EmbeddingService, SummarizerService


ShortTermFactory = Callable[[str], ShortTermMemoryProtocol]


class MemoryRouter:
    def __init__(
        self,
        *,
        short_term_factory: ShortTermFactory,
        long_term: LongTermMemory,
        embedder: EmbeddingService,
        summarizer: SummarizerService,
    ) -> None:
        self.short_term_factory = short_term_factory
        self.long_term = long_term
        self.embedder = embedder
        self.summarizer = summarizer

    async def get_context(self, session_id: str, user_id: str, query: str) -> MemoryContext:
        recent = await self.short_term_factory(session_id).get_history(last_n=10)
        query_embedding = await self.embedder.embed(query)
        fragments = self.long_term.search_similar(
            user_id=user_id,
            query_embedding=query_embedding,
            top_k=5,
        )
        return MemoryContext(
            recent=recent,
            long_term=[MemoryFragmentRead.model_validate(fragment) for fragment in fragments],
        )

    async def append_turn(self, session_id: str, user_message: str, assistant_message: str) -> None:
        stm = self.short_term_factory(session_id)
        await stm.append({"role": "user", "content": user_message})
        await stm.append({"role": "assistant", "content": assistant_message})
        self.long_term.add_message(session_id, "user", user_message)
        self.long_term.add_message(session_id, "assistant", assistant_message)

    async def consolidate(self, session_id: str, user_id: str) -> str | None:
        stm = self.short_term_factory(session_id)
        history = await stm.get_history()
        if not history:
            history = [
                {"role": message.role, "content": message.content}
                for message in self.long_term.get_history(session_id)
            ]
        summary = (await self.summarizer.summarize(history)).strip()
        if not summary:
            return None
        embedding = await self.embedder.embed(summary)
        self.long_term.save_fragment(
            user_id=user_id,
            content=summary,
            embedding=embedding,
            source_session=session_id,
        )
        await stm.clear()
        return summary
