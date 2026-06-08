from app.repositories.reminder_repository import ReminderRepository
from app.schemas.notes_reminders import ReminderCreate, ReminderRead, ReminderUpdate


class ReminderNotFoundError(Exception):
    pass


class ReminderService:
    def __init__(self, repository: ReminderRepository) -> None:
        self.repository = repository

    def create(self, payload: ReminderCreate) -> ReminderRead:
        reminder = self.repository.create(
            user_id=payload.user_id,
            title=payload.title,
            description=payload.description,
            due_at=payload.due_at,
            priority=payload.priority,
            recurring=payload.recurring,
        )
        return ReminderRead.model_validate(reminder)

    def get(self, reminder_id: str) -> ReminderRead:
        reminder = self.repository.get(reminder_id)
        if reminder is None:
            raise ReminderNotFoundError(reminder_id)
        return ReminderRead.model_validate(reminder)

    def list_by_user(self, user_id: str, *, include_completed: bool = False) -> list[ReminderRead]:
        reminders = self.repository.list_by_user(user_id, include_completed=include_completed)
        return [ReminderRead.model_validate(r) for r in reminders]

    def get_due_soon(self, user_id: str) -> list[ReminderRead]:
        reminders = self.repository.get_due_soon(user_id)
        return [ReminderRead.model_validate(r) for r in reminders]

    def update(self, reminder_id: str, updates: ReminderUpdate) -> ReminderRead:
        reminder = self.repository.get(reminder_id)
        if reminder is None:
            raise ReminderNotFoundError(reminder_id)
        updated = self.repository.update(reminder, **updates.model_dump(exclude_unset=True))
        return ReminderRead.model_validate(updated)

    def delete(self, reminder_id: str) -> None:
        reminder = self.repository.get(reminder_id)
        if reminder is None:
            raise ReminderNotFoundError(reminder_id)
        self.repository.delete(reminder)
