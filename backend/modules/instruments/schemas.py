from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime


class HeartbeatIn(BaseModel):
    instrument_id: str = Field(..., min_length=1, max_length=128)
    name: str = Field(..., min_length=1, max_length=255)
    status: str = "online"
    lab_id: UUID | None = None
    company_id: UUID | None = None


class InstrumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    instrument_id: str
    name: str
    lab_id: UUID | None
    status: str
    last_seen_at: datetime
    created_at: datetime


class InstrumentCommand(BaseModel):
    id: str
    type: str
    payload: dict | None = None


class InstrumentFileOut(BaseModel):
    object_key: str
    filename: str
    instrument_id: str
    uploaded_at: str | None
    size_bytes: int | None
    content_type: str
