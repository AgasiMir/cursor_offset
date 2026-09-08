from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.utils.pagination import Pagination


class PostReadSchema(BaseModel):
    id: UUID
    title: str
    content: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PostReadSchemaWithPagination(BaseModel):
    posts: list[PostReadSchema]
    posts_on_page: int = Field(description="Количество постов на возвращённой странице")
    pagination: Pagination


class Cursor(BaseModel):
    id: UUID
    created_at: datetime


class PostReadSchemaWithCursor(BaseModel):
    posts: list[PostReadSchema]
    total_count: int | None = Field(description="Общее количество постов")
    has_more: bool
    next_cursor: Cursor | None = None


class PostCreateSchema(BaseModel):
    title: str = Field(min_length=1, max_length=120, description="Заголовок поста")
    content: str | None = Field(default=None, description="Содержимое поста")


class PostPartialUpdateSchema(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=120,
        description="Заголовок поста",
    )
    content: str | None = Field(default=None, description="Содержимое поста")
