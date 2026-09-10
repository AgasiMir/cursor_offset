from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Query
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from app.core.database import async_session
from app.schemas import CursorPaginationSchema, Pagination
from app.service.post_service import PostService
from app.uow import UnitOfWork


async def get_db():
    async with UnitOfWork(session_factory=async_session) as session:
        yield session


DBDep = Annotated[UnitOfWork, Depends(get_db)]
PaginationDep = Annotated[Pagination, Depends()]


async def get_cursor_pagination(
    limit: int = Query(default=5, ge=1, le=50, description="Количество постов на странице"),
    cursor_id: UUID | None = Query(default=None),  # noqa: B008
    created_at: datetime | None = Query(default=None),  # noqa: B008
) -> CursorPaginationSchema:
    try:
        return CursorPaginationSchema(limit=limit, cursor_id=cursor_id, created_at=created_at)
    except ValidationError as e:
        raise RequestValidationError(errors=e.errors()) from e


CursorPaginationDep = Annotated[CursorPaginationSchema, Depends(get_cursor_pagination)]


async def get_post_service(uow: DBDep) -> PostService:
    return PostService(uow=uow)


PostServiceDep = Annotated[PostService, Depends(get_post_service)]
