from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class PersonalityCreate(BaseModel):
    trust: int = Field(default=50, ge=0, le=100)
    respect: int = Field(default=50, ge=0, le=100)
    warmth: int = Field(default=50, ge=0, le=100)
    curiosity: int = Field(default=50, ge=0, le=100)
    fear: int = Field(default=10, ge=0, le=100)
    loyalty: int = Field(default=50, ge=0, le=100)
    aggression: int = Field(default=20, ge=0, le=100)


class NPCCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    role: str = Field(..., min_length=1, max_length=100)
    location: str = Field(..., min_length=1, max_length=100)
    personality: Optional[PersonalityCreate] = None


class NPCResponse(BaseModel):
    id: str
    name: str
    role: str
    location: str

    model_config = ConfigDict(from_attributes=True)

