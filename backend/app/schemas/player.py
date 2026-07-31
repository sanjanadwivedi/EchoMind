from pydantic import BaseModel, ConfigDict, Field


class PlayerCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=100)


class PlayerResponse(BaseModel):
    id: str
    username: str

    model_config = ConfigDict(from_attributes=True)
