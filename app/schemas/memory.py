from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class MessageRole(StrEnum):
    user = "user"
    assistant = "assistant"
    system = "system"


class SessionCreate(BaseModel):
    user_id: str = Field(min_length=1, max_length=100)


class SessionRead(BaseModel):
    id: str
    user_id: str
    created_at: datetime
    last_active: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1)


class ChatResponse(BaseModel):
    session_id: str
    response: str
    used_long_term_memory: list[str]


class MessageRead(BaseModel):
    id: str
    session_id: str
    role: MessageRole
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MemoryFragmentRead(BaseModel):
    id: str
    user_id: str
    content: str
    source_session: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MemoryContext(BaseModel):
    recent: list[dict]
    long_term: list[MemoryFragmentRead]
