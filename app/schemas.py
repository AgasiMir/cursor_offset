from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Pagination(BaseModel):
    page: int = Field(default=1, ge=1, description="Номер страницы")
    page_size: int = Field(default=5, ge=1, le=50, description="Количество постов на странице")


class PostReadSchema(BaseModel):
    id: UUID
    title: str
    content: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PostReadSchemaWithPagination(BaseModel):
    posts: list[PostReadSchema]
    pagination: Pagination


class CursorReadSchema(BaseModel):
    last_id: UUID
    last_created_at: datetime


class CursorPaginationSchema(BaseModel):
    limit: int = Field(default=5, ge=1, le=50, description="Количество постов на странице")
    cursor_id: UUID | None = None
    created_at: datetime | None = None

    @model_validator(mode="after")
    def validate_cursor(self):
        if self.cursor_id is None and self.created_at is not None:
            raise ValueError("cursor_id must be provided if created_at is provided")
        if self.cursor_id is not None and self.created_at is None:
            raise ValueError("created_at must be provided if cursor_id is provided")

        return self

    model_config = ConfigDict(from_attributes=True)


class PostReadSchemaWithCursor(BaseModel):
    posts: list[PostReadSchema]
    has_more: bool
    next_cursor: CursorReadSchema | None = None


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
