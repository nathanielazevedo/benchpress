from pydantic import BaseModel
from typing import Any


class AIAction(BaseModel):
    type: str
    node: dict | None = None
    edge: dict | None = None
    id: str | None = None
    data: dict | None = None


class AIChatRequest(BaseModel):
    message: str
    nodes: list[Any]
    edges: list[Any]


class AIChatResponse(BaseModel):
    message: str
    actions: list[AIAction]
