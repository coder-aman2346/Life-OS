from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ── Notes ──────────────────────────────────────────────────────


class NoteCreate(BaseModel):
    user_id: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=255)
    body: str = ""
    tags: str = ""  # comma-separated
    pinned: bool = False


class NoteUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    body: str | None = None
    tags: str | None = None
    pinned: bool | None = None


class NoteRead(BaseModel):
    id: str
    user_id: str
    title: str
    body: str
    tags: str
    pinned: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── Reminders ──────────────────────────────────────────────────


class ReminderCreate(BaseModel):
    user_id: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=255)
    description: str = ""
    due_at: datetime | None = None
    priority: int = Field(default=0, ge=0, le=3)
    recurring: str | None = None


class ReminderUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    description: str | None = None
    due_at: datetime | None = None
    completed: bool | None = None
    priority: int | None = Field(default=None, ge=0, le=3)
    recurring: str | None = None


class ReminderRead(BaseModel):
    id: str
    user_id: str
    title: str
    description: str
    due_at: datetime | None
    completed: bool
    priority: int
    recurring: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
