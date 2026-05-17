from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2000)


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    done: bool | None = None


class TaskRead(BaseModel):
    id: int
    title: str
    description: str | None
    done: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RootResponse(BaseModel):
    service: str
    environment: str
    docs: str
    health: dict[str, str]


class HealthResponse(BaseModel):
    status: str
    environment: str
    database: str | None = None
