from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MemoryResponse(BaseModel):
    id: str
    summary: str
    category: str
    state: str
    importance: float
    confidence: float
    recall_count: int
    last_recalled_at: datetime | None
    created_at: datetime
    event_type: str
    emotion: str
    location: str | None
    embedding_id: str
    context: dict

    model_config = ConfigDict(from_attributes=True)


class ReflectionResponse(BaseModel):
    memory_count: int
    input_memories: list[str]
    reflection: str | None
