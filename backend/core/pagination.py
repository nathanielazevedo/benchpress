from fastapi import Query
from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar("T")


class PageParams:
    def __init__(
        self,
        skip: int = Query(default=0, ge=0, description="Number of records to skip"),
        limit: int = Query(default=50, ge=1, le=200, description="Max records to return"),
    ):
        self.skip = skip
        self.limit = limit


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    skip: int
    limit: int
