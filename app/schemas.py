from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Pagination(BaseModel):
    """
    Схема пагинации для запросов с поддержкой постраничной навигации.

    Используется для разделения списков сущностей (например, постов)
    на страницы с настраиваемым номером и размером страницы.

    Attributes:
        page: Номер страницы (начиная с 1). По умолчанию — 1.
        page_size: Количество записей на странице. По умолчанию — 5,
            допустимый диапазон: от 1 до 50.
    """

    page: int = Field(default=1, ge=1, description="Номер страницы")
    page_size: int = Field(default=5, ge=1, le=50, description="Количество постов на странице")


class PostReadSchema(BaseModel):
    """
    Схема для чтения данных о посте.

    Используется для сериализации ответа API с полями поста.
    Настроена через `from_attributes=True` для корректного маппинга
    с ORM-моделями SQLAlchemy.

    Attributes:
        id: UUID идентификатор поста.
        title: Заголовок поста.
        content: Содержимое поста. Может быть None.
        created_at: Дата и время создания поста.
    """

    id: UUID
    title: str
    content: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PostReadSchemaWithPagination(BaseModel):
    """
    Схема ответа API для пагинации списка постов.

    Содержит сам список постов и метаданные пагинации
    (текущая страница, размер страницы).

    Attributes:
        posts: Список постов в формате PostReadSchema.
        pagination: Объект пагинации с информацией о странице.
    """

    posts: list[PostReadSchema]
    pagination: Pagination


class CursorReadSchema(BaseModel):
    """
    Схема для передачи курсора при курсорной пагинации.

    Используется для указания позиции в списке постов
    (последний полученный пост), чтобы запросить следующую порцию.

    Attributes:
        last_id: UUID последнего поста в текущей порции.
        last_created_at: Дата создания последнего поста.
    """

    last_id: UUID
    last_created_at: datetime


class CursorPaginationSchema(BaseModel):
    """
    Схема пагинации с использованием курсора.

    Используется для запросов постраничной навигации, где каждая страница
    определяется позицией (курсором) в упорядоченном списке постов.
    Курсор состоит из UUID последнего полученного поста и даты его создания,
    что обеспечивает стабильную навигацию даже при изменениях в данных.

    Attributes:
        limit: Количество постов на странице. По умолчанию — 5,
            допустимый диапазон: от 1 до 50.
        cursor_id: UUID поста, с которого начинается следующая порция.
            Не обязателен для первого запроса.
            Должен указываться вместе с created_at.
        created_at: Дата создания поста-курсора.
            Не обязателен для первого запроса.
            Должен указываться вместе с cursor_id.
    """

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


class PostReadSchemaWithCursor(BaseModel):
    """
    Схема ответа API для курсорной пагинации списка постов.

    Используется вместо `PostReadSchemaWithPagination` при навигации
    через курсор. Содержит список постов за текущую страницу, флаг,
    указывающий наличие дополнительных записей, и объект курсора
    для запроса следующей порции.

    Attributes:
        posts: Список постов в формате PostReadSchema.
        has_more: True, если в списке есть ещё записи после текущей страницы.
        next_cursor: Курсор для получения следующей порции постов.
            Содержит UUID и дату создания последнего поста в текущей порции.
            Равно None, если дополнительных записей нет (has_more=False).
    """

    posts: list[PostReadSchema]
    has_more: bool
    next_cursor: CursorReadSchema | None = None


class PostCreateSchema(BaseModel):
    """
    Схема для создания нового поста.

    Используется для валидации входных данных при создании записи.
    Заголовок проходит дополнительную валидацию через field_validator,
    которая обрезает пробелы и проверяет, что поле не пустое.

    Attributes:
        title: Заголовок поста. Обязательное поле, длина от 1 до 120 символов.
            Не может состоять только из пробелов.
        content: Содержимое поста. Необязательное поле, может быть None.
    """

    title: str = Field(min_length=1, max_length=120, description="Заголовок поста")
    content: str | None = Field(default=None, description="Содержимое поста")

    @field_validator("title", mode="before")
    def title_must_be_not_empty(cls, v):
        if not isinstance(v, str):
            raise TypeError("title should have type string.")

        v = v.strip()
        if len(v) == 0:
            raise ValueError("Title cannot be empty")

        return v


class PostPartialUpdateSchema(BaseModel):
    """
    Схема для частичного обновления поста (PATCH-запрос).

    Используется для валидации входных данных при обновлении записи.
    Все поля необязательные — передаются только те, которые нужно изменить.
    Заголовок проходит дополнительную валидацию через field_validator,
    которая обрезает пробелы и проверяет, что поле не пустое.

    Attributes:
        title: Заголовок поста. Необязательное поле, длина от 1 до 120 символов.
            Не может состоять только из пробелов. Если не передано — поле не обновляется.
        content: Содержимое поста. Необязательное поле, может быть None.
            Если не передано — поле не обновляется.
    """

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=120,
        description="Заголовок поста",
    )
    content: str | None = Field(default=None, description="Содержимое поста")

    @field_validator("title", mode="before")
    def title_must_be_not_empty(cls, v):
        if not isinstance(v, str):
            raise TypeError("title should have type string.")

        v = v.strip()
        if len(v) == 0:
            raise ValueError("Title cannot be empty")

        return v
