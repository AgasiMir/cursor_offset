from typing import Annotated

from fastapi import Depends

from app.core.database import async_session
from app.service.post_service import PostService
from app.uow import UnitOfWork
from app.utils.pagination import Pagination


async def get_db():
    async with UnitOfWork(session_factory=async_session) as session:
        yield session


DBDep = Annotated[UnitOfWork, Depends(get_db)]
PaginationDep = Annotated[Pagination, Depends()]


async def get_post_service(uow: DBDep) -> PostService:
    return PostService(uow=uow)


PostServiceDep = Annotated[PostService, Depends(get_post_service)]
