from app.repositories.note_repository import NoteRepository
from app.schemas.notes_reminders import NoteCreate, NoteRead, NoteUpdate


class NoteNotFoundError(Exception):
    pass


class NoteService:
    def __init__(self, repository: NoteRepository) -> None:
        self.repository = repository

    def create(self, payload: NoteCreate) -> NoteRead:
        note = self.repository.create(
            user_id=payload.user_id,
            title=payload.title,
            body=payload.body,
            tags=payload.tags,
            pinned=payload.pinned,
        )
        return NoteRead.model_validate(note)

    def get(self, note_id: str) -> NoteRead:
        note = self.repository.get(note_id)
        if note is None:
            raise NoteNotFoundError(note_id)
        return NoteRead.model_validate(note)

    def list_by_user(self, user_id: str) -> list[NoteRead]:
        notes = self.repository.list_by_user(user_id)
        return [NoteRead.model_validate(n) for n in notes]

    def update(self, note_id: str, updates: NoteUpdate) -> NoteRead:
        note = self.repository.get(note_id)
        if note is None:
            raise NoteNotFoundError(note_id)
        updated = self.repository.update(note, **updates.model_dump(exclude_unset=True))
        return NoteRead.model_validate(updated)

    def delete(self, note_id: str) -> None:
        note = self.repository.get(note_id)
        if note is None:
            raise NoteNotFoundError(note_id)
        self.repository.delete(note)

    def search(self, user_id: str, query: str) -> list[NoteRead]:
        notes = self.repository.search(user_id, query)
        return [NoteRead.model_validate(n) for n in notes]
