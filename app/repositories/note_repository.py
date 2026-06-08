from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.notes import NoteRecord


class NoteRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, *, user_id: str, title: str, body: str, tags: str, pinned: bool) -> NoteRecord:
        note = NoteRecord(user_id=user_id, title=title, body=body, tags=tags, pinned=pinned)
        self.db.add(note)
        self.db.commit()
        self.db.refresh(note)
        return note

    def get(self, note_id: str) -> NoteRecord | None:
        return self.db.get(NoteRecord, note_id)

    def list_by_user(self, user_id: str) -> list[NoteRecord]:
        statement = (
            select(NoteRecord)
            .where(NoteRecord.user_id == user_id)
            .order_by(NoteRecord.pinned.desc(), NoteRecord.updated_at.desc())
        )
        return list(self.db.scalars(statement))

    def update(self, note: NoteRecord, **fields: object) -> NoteRecord:
        for key, value in fields.items():
            if value is not None:
                setattr(note, key, value)
        self.db.add(note)
        self.db.commit()
        self.db.refresh(note)
        return note

    def delete(self, note: NoteRecord) -> None:
        self.db.delete(note)
        self.db.commit()

    def search(self, user_id: str, query: str) -> list[NoteRecord]:
        """Simple case-insensitive text search over title and body."""
        pattern = f"%{query}%"
        statement = (
            select(NoteRecord)
            .where(
                NoteRecord.user_id == user_id,
                (NoteRecord.title.ilike(pattern)) | (NoteRecord.body.ilike(pattern)),
            )
            .order_by(NoteRecord.updated_at.desc())
        )
        return list(self.db.scalars(statement))
