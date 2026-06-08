from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.memory import MemoryFragmentRecord, MessageRecord, SessionRecord, utc_now


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right:
        return 0.0
    size = min(len(left), len(right))
    dot = sum(left[i] * right[i] for i in range(size))
    left_norm = sum(value * value for value in left[:size]) ** 0.5
    right_norm = sum(value * value for value in right[:size]) ** 0.5
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


class MemoryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_session(self, user_id: str) -> SessionRecord:
        session = SessionRecord(user_id=user_id)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_session(self, session_id: str) -> SessionRecord | None:
        return self.db.get(SessionRecord, session_id)

    def touch_session(self, session: SessionRecord) -> SessionRecord:
        session.last_active = utc_now()
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def add_message(self, session_id: str, role: str, content: str) -> MessageRecord:
        message = MessageRecord(session_id=session_id, role=role, content=content)
        self.db.add(message)
        session = self.get_session(session_id)
        if session is not None:
            session.last_active = utc_now()
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_messages(self, session_id: str, limit: int | None = None) -> list[MessageRecord]:
        statement = (
            select(MessageRecord)
            .where(MessageRecord.session_id == session_id)
            .order_by(MessageRecord.created_at.asc())
        )
        if limit:
            statement = statement.limit(limit)
        return list(self.db.scalars(statement))

    def save_fragment(
        self,
        *,
        user_id: str,
        content: str,
        embedding: list[float],
        source_session: str | None,
    ) -> MemoryFragmentRecord:
        fragment = MemoryFragmentRecord(
            user_id=user_id,
            content=content,
            embedding=embedding,
            source_session=source_session,
        )
        self.db.add(fragment)
        self.db.commit()
        self.db.refresh(fragment)
        return fragment

    def list_fragments(self, user_id: str) -> list[MemoryFragmentRecord]:
        statement = (
            select(MemoryFragmentRecord)
            .where(MemoryFragmentRecord.user_id == user_id)
            .order_by(MemoryFragmentRecord.created_at.desc())
        )
        return list(self.db.scalars(statement))

    def search_fragments(
        self, *, user_id: str, embedding: list[float], top_k: int = 5
    ) -> list[MemoryFragmentRecord]:
        if self.db.bind and self.db.bind.dialect.name == "postgresql":
            distance = MemoryFragmentRecord.embedding.op("<=>")(embedding)
            statement = (
                select(MemoryFragmentRecord)
                .where(MemoryFragmentRecord.user_id == user_id)
                .order_by(distance)
                .limit(top_k)
            )
            return list(self.db.scalars(statement))

        fragments = self.list_fragments(user_id)
        return sorted(
            fragments,
            key=lambda fragment: cosine_similarity(list(fragment.embedding), embedding),
            reverse=True,
        )[:top_k]

    def forget_user_memory(self, user_id: str) -> int:
        result = self.db.execute(
            delete(MemoryFragmentRecord).where(MemoryFragmentRecord.user_id == user_id)
        )
        self.db.commit()
        return int(result.rowcount or 0)

    def delete_session(self, session: SessionRecord) -> None:
        self.db.delete(session)
        self.db.commit()
