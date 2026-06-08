from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.reminders import ReminderRecord


class ReminderRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        user_id: str,
        title: str,
        description: str,
        due_at: datetime | None,
        priority: int,
        recurring: str | None,
    ) -> ReminderRecord:
        reminder = ReminderRecord(
            user_id=user_id,
            title=title,
            description=description,
            due_at=due_at,
            priority=priority,
            recurring=recurring,
        )
        self.db.add(reminder)
        self.db.commit()
        self.db.refresh(reminder)
        return reminder

    def get(self, reminder_id: str) -> ReminderRecord | None:
        return self.db.get(ReminderRecord, reminder_id)

    def list_by_user(
        self,
        user_id: str,
        *,
        include_completed: bool = False,
    ) -> list[ReminderRecord]:
        statement = select(ReminderRecord).where(ReminderRecord.user_id == user_id)
        if not include_completed:
            statement = statement.where(ReminderRecord.completed == False)  # noqa: E712
        statement = statement.order_by(
            ReminderRecord.completed.asc(),
            ReminderRecord.priority.desc(),
            ReminderRecord.due_at.asc().nullslast(),
        )
        return list(self.db.scalars(statement))

    def get_due_soon(self, user_id: str) -> list[ReminderRecord]:
        """Return uncompleted reminders with a due_at in the past or present."""
        now = datetime.now(timezone.utc)
        statement = (
            select(ReminderRecord)
            .where(
                ReminderRecord.user_id == user_id,
                ReminderRecord.completed == False,  # noqa: E712
                ReminderRecord.due_at <= now,
            )
            .order_by(ReminderRecord.due_at.asc())
        )
        return list(self.db.scalars(statement))

    def update(self, reminder: ReminderRecord, **fields: object) -> ReminderRecord:
        for key, value in fields.items():
            if value is not None:
                setattr(reminder, key, value)
        self.db.add(reminder)
        self.db.commit()
        self.db.refresh(reminder)
        return reminder

    def delete(self, reminder: ReminderRecord) -> None:
        self.db.delete(reminder)
        self.db.commit()
