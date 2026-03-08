from pydantic import BaseModel, ConfigDict, Field, field_validator
from uuid import UUID
from datetime import datetime

from modules.companies.schemas import CompanyOut


class LabCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    company_id: UUID

    @field_validator("name", mode="before")
    @classmethod
    def strip_name(cls, v: str) -> str:
        return v.strip() if isinstance(v, str) else v


class LabUpdate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)

    @field_validator("name", mode="before")
    @classmethod
    def strip_name(cls, v: str) -> str:
        return v.strip() if isinstance(v, str) else v


class LabOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    company_id: UUID
    created_at: datetime


class LabWithCompanyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    company: CompanyOut
    created_at: datetime
