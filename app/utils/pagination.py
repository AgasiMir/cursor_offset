from enum import IntEnum

from pydantic import BaseModel, Field


class PageSize(IntEnum):
    SMALL = 5
    MEDIUM = 10
    LARGE = 20


class Pagination(BaseModel):
    page: int = Field(default=1, ge=1, description="Номер страницы")
    page_size: int = Field(default=5, ge=1, le=50, description="Размер страницы")
