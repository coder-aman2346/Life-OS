from app.repositories.memory_repository import MemoryRepository


class SessionNotFoundError(Exception):
    pass


class LongTermMemory:
    def __init__(self, repository: MemoryRepository) -> None:
        self.repository = repository

    def create_session(self, user_id: str):
        return self.repository.create_session(user_id)

    def get_session(self, session_id: str):
        session = self.repository.get_session(session_id)
        if session is None:
            raise SessionNotFoundError(session_id)
        return session

    def add_message(self, session_id: str, role: str, content: str):
        self.get_session(session_id)
        return self.repository.add_message(session_id, role, content)

    def get_history(self, session_id: str):
        self.get_session(session_id)
        return self.repository.get_messages(session_id)

    def save_fragment(
        self,
        *,
        user_id: str,
        content: str,
        embedding: list[float],
        source_session: str | None,
    ):
        return self.repository.save_fragment(
            user_id=user_id,
            content=content,
            embedding=embedding,
            source_session=source_session,
        )

    def list_fragments(self, user_id: str):
        return self.repository.list_fragments(user_id)

    def search_similar(self, *, user_id: str, query_embedding: list[float], top_k: int = 5):
        return self.repository.search_fragments(
            user_id=user_id,
            embedding=query_embedding,
            top_k=top_k,
        )

    def forget_user_memory(self, user_id: str) -> int:
        return self.repository.forget_user_memory(user_id)

    def delete_session(self, session_id: str) -> None:
        session = self.get_session(session_id)
        self.repository.delete_session(session)
