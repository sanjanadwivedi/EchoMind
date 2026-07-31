from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    npc_id: UUID
    player_id: UUID
    message: str = Field(..., min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    response: str
    emotion: str = "Neutral"
    telemetry: Optional[Dict[str, Any]] = None
